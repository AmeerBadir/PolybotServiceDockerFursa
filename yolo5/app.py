import time
from pathlib import Path
from flask import Flask, request
from detect import run
import uuid
import yaml
from loguru import logger
import os
import boto3
from pymongo import MongoClient

images_bucket = os.environ['BUCKET_NAME']

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']

app = Flask(__name__)

mongo_client = MongoClient('mongodb://mongo1:27017/')
db = mongo_client['yolov5_predictions']
predictions_collection = db['predictions']
session = boto3.Session()
s3 = session.client('s3', 'us-east-1')


@app.route('/predict', methods=['POST'])
def predict():
    # Generates a UUID for this current prediction HTTP request. This id can be used as a reference in logs to identify and track individual prediction requests.
    prediction_id = str(uuid.uuid4())
    logger.info(f'prediction: {prediction_id}. start processing')
    # Receives a URL parameter representing the image to download from S3
    img_name = request.args.get('imgName')
    try:
        local_file_name = f'{img_name}'
        s3.download_file(images_bucket, img_name, local_file_name)
    except s3.exceptions.NoSuchKey:
        return f'image {img_name} did not exist in bucket', 404

    original_img_path = local_file_name

    logger.info(f'prediction: {prediction_id}/{original_img_path}. Download img completed')

    # Predicts the objects in the image
    run(
        weights='yolov5s.pt',
        data='data/coco128.yaml',
        source=original_img_path,
        project='static/data',
        name=prediction_id,
        save_txt=True
    )

    logger.info(f'prediction: {prediction_id}/{original_img_path}. done')

    # This is the path for the predicted image with labels The predicted image typically includes bounding boxes
    # drawn around the detected objects, along with class labels and possibly confidence scores.

    predicted_img_path = Path(f'static/data/{prediction_id}/{original_img_path}')

    # Uploads the predicted image (predicted_img_path) to S3.
    predict_img_path = f'{img_name.split(".")[0]}_predicted.{img_name.split(".")[1]}'
    try:
        s3.upload_file(predicted_img_path, images_bucket, predict_img_path)
    except Exception as e:
        logger.error(f'prediction: {prediction_id}. failed uploading image to S3: {e}')

    # Parse prediction labels and create a summary
    pred_summary_path = Path(f'static/data/{prediction_id}/labels/{original_img_path.split(".")[0]}.txt')
    if pred_summary_path.exists():
        with open(pred_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

        prediction_summary = {
            'prediction_id': prediction_id,
            'original_img_path': original_img_path,
            'predicted_img_path': str(predicted_img_path),
            'labels': labels,
            'time': time.time()
        }

        try:
            result = predictions_collection.insert_one(prediction_summary)
            logger.info(f'prediction: {prediction_id}/{img_name}. Stored in MongoDB with _id: {result.inserted_id}')
        except Exception as e:
            logger.error(f'prediction: {prediction_id}/{img_name}. Failed to store in MongoDB: {e}')
        return str(prediction_summary)
    else:
        return f'prediction: {prediction_id}/{original_img_path}. prediction result not found', 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
