import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import requests
import boto3
import json
from collections import Counter


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60, certificate=open("cert.pem", "r"))

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


def get_result(respond):
    if "labels" in respond:
        try:
            dict_objects = dict()
            total_count = 0
            for lab in respond['labels']:
                item_class = lab['class']
                if item_class in dict_objects:
                    dict_objects[item_class] += 1
                else:
                    dict_objects[item_class] = 1
                total_count += 1
            return total_count, dict_objects
        except Exception as e:
            logger.error(f"Error in get_result function: {e}")
            return None, {}


def summary_msg(total_object_number, object_dictionary):
    msg = f'We detect {total_object_number} objects.\n'
    for key, val in object_dictionary.items:
        object_count = f'object {key} found {val} times.\n'
        msg += object_count
    return msg


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        if "text" in msg:
            if msg["text"] == '/start':
                self.send_text(msg['chat']['id'], 'Hi!, give a photo to start object detection')
        if self.is_current_msg_photo(msg):
            # TODO upload the photo to S3

            photo_path = self.download_user_photo(msg)
            img_name = os.path.basename(photo_path)
            s3 = boto3.client('s3')
            images_bucket = os.environ['BUCKET_NAME']
            try:
                s3.upload_file(photo_path, images_bucket, img_name)
            except Exception as e:
                self.send_text(msg['chat']['id'], "failed to upload image")

                logger.error(f"Upload image to s3 failed: {e}")

            # TODO send an HTTP request to the `yolo5` service for prediction

            try:
                yolo_url = f"http://yolo5-container:8081/predict?imgName={img_name}"
                response = requests.post(yolo_url)
                if response.status_code == 200:
                    prediction_result = response.json()
                    logger.info(f'YOLO prediction result: {prediction_result}')
                else:
                    return
            except Exception as e:
                self.send_text(msg['chat']['id'], "failed to connect to yolo service")
                logger.error(f'Error communicating with YOLO service: {str(e)}')
                return

            # TODO send the returned results to the Telegram end-user
            total_object_number, object_dictionary = get_result(response.json())
            if total_object_number is None and object_dictionary == {}:
                self.send_text(msg['chat']['id'], "failed to upload image")
            else:
                response_msg = summary_msg(total_object_number,object_dictionary)
                self.send_text(msg['chat']['id'], response_msg)

        else:
            self.send_text(msg['chat']['id'], 'Please send a photo for object detection.')
