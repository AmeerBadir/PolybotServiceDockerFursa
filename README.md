# The Polybot Service: Docker Project

# Overview

This project is a personal development initiative aimed at building a containerized microservices architecture for an AI-powered image processing service. The service extends a previous Python-based chatbot to include object detection using the YOLOv5 deep learning model. The project is designed, developed, and deployed entirely by me.

# Project Components

The service consists of multiple containerized microservices:

 - polybot: A Telegram bot that handles image submissions from users.

- yolo5: An object detection service based on the YOLOv5 pre-trained deep learning model.

- mongo: A MongoDB database cluster for storing processed image data.

# Getting Started

# Clone the Repository

 git clone https://github.com/AmeerBadir/PolybotServiceDockerFursa.git

# Set Up a Virtual Environment (Recommended)

- Creating an isolated Python virtual environment for this project is a good practice:

- python -m venv venv
- source venv/bin/activate   # On macOS/Linux
- venv\Scripts\activate     # On Windows

# Running the Project with Docker Compose

The entire service can be launched using Docker Compose:

docker compose up

Configuration

- Environment variables are stored in an .env file to allow easy deployment in different environments:

# .env file
POLYBOT_IMG_NAME=polybot:v1.0
YOLO5_IMG_NAME=yolo5:v1.0
TELEGRAM_APP_URL=https://my-polybot-service.com

# Microservices Details

 - MongoDB (mongo):
    MongoDB is used to store image metadata and detection results. A high-availability (HA) MongoDB cluster is configured using Docker, ensuring data persistence and fault tolerance.

- YOLOv5 (yolo5): The yolo5 service provides object detection capabilities using the YOLOv5 model. The service is implemented as a Flask-based API with an endpoint:

POST /predict?imgName=example.jpg

The imgName parameter represents an image stored in an AWS S3 bucket. The service downloads the image, performs object detection, and returns results in JSON format.

Example JSON output:

{
    "prediction_id": "12345678-abcd-efgh-ijkl-1234567890ab",
    "original_img_path": "data/images/example.jpg",
    "predicted_img_path": "static/data/12345678-abcd-efgh-ijkl-1234567890ab/example.jpg",
    "labels": [
      {"class": "car", "cx": 0.5, "cy": 0.6, "height": 0.2, "width": 0.3},
      {"class": "person", "cx": 0.3, "cy": 0.7, "height": 0.1, "width": 0.2}
    ],
    "time": 1692016473.2343626
}

# Telegram Bot (polybot)

The Telegram bot allows users to submit images and receive detected objects in response. The integration flow is as follows:

Users send images to the bot.

The bot uploads images to an S3 bucket.

The bot sends a request to yolo5 for object detection.

The bot parses the response and sends the detection results back to the user.

# Deployment

This project is deployed on an AWS EC2 instance using Docker Compose. Both development and production environments use the same docker-compose.yaml file with environment-specific variables defined in an .env file.

# Deployment Notes

The Telegram bot is exposed via a secure HTTPS endpoint.

Docker images are pushed to a public DockerHub repository.

The EC2 instance is assigned an IAM role with permissions for S3 access.

Secrets such as the Telegram bot token are managed securely using Docker secrets.

The MongoDB cluster is initialized automatically at startup.

# CI/CD Pipeline

The project integrates a GitHub Actions-based CI/CD pipeline that automates testing, building, and deployment. The workflows are defined in:

.github/workflows/service-deploy-dev.yaml
.github/workflows/service-deploy-prod.yaml

# The pipeline includes:

Automated testing after every push.

Image building and deployment to DockerHub.

Secure deployment to AWS EC2 using SSH keys and environment secrets.

# Security Considerations

No AWS credentials are hardcoded. AWS authentication is handled through IAM roles.

Docker images are scanned for vulnerabilities using snyk.

API endpoints have timeout and retry mechanisms to improve fault tolerance.

Sensitive data (e.g., Telegram token) is stored securely.

# Summary

This project demonstrates my ability to design, develop, and deploy a robust, containerized microservices system integrating AI-powered object detection. The system is fully automated, highly scalable, and production-ready.

Contact

For any inquiries or collaboration, feel free to reach out via GitHub or email.

Developed and maintained by Ameer Badir




<img src="https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_street.jpeg" width="60%">

```json
{
    "prediction_id": "9a95126c-f222-4c34-ada0-8686709f6432",
    "original_img_path": "data/images/street.jpeg",
    "predicted_img_path": "static/data/9a95126c-f222-4c34-ada0-8686709f6432/street.jpeg",
    "labels": [
      {
        "class": "person",
        "cx": 0.0770833,
        "cy": 0.673675,
        "height": 0.0603291,
        "width": 0.0145833
      },
      {
        "class": "traffic light",
        "cx": 0.134375,
        "cy": 0.577697,
        "height": 0.0329068,
        "width": 0.0104167
      },
      {
        "class": "potted plant",
        "cx": 0.984375,
        "cy": 0.778793,
        "height": 0.095064,
        "width": 0.03125
      },
      {
        "class": "stop sign",
        "cx": 0.159896,
        "cy": 0.481718,
        "height": 0.0859232,
        "width": 0.053125
      },
      {
        "class": "car",
        "cx": 0.130208,
        "cy": 0.734918,
        "height": 0.201097,
        "width": 0.108333
      },
      {
        "class": "bus",
        "cx": 0.285417,
        "cy": 0.675503,
        "height": 0.140768,
        "width": 0.0729167
      }
    ],
    "time": 1692016473.2343626
}
```

<img src="https://alonitac.github.io/DevOpsTheHardWay/img/docker_project_polysample.jpg" width="30%">

