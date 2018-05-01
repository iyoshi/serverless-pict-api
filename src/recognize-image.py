import decimal
import json
import logging
import os
from urllib import parse

import boto3

from src.decimalencoder import DecimalEncoder

s3 = boto3.resource('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    images_bucket = event['Records'][0]['s3']['bucket']['name']
    images_key = parse.unquote_plus(event['Records'][0]['s3']['object']['key'], 'utf8')
    try:
        labels = rekognition.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': images_bucket,
                    'Name': images_key,
                },
            },
            MinConfidence=75
        )

        faces = rekognition.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': images_bucket,
                    'Name': images_key,
                },
            },
            Attributes=['ALL']
        )

        rekognized_labels = { 'Labels': labels['Labels'], 'FaceDetails': faces['FaceDetails'] }
        logger.info(json.dumps(rekognized_labels))

        photo_id = images_key.split('.')[0]
        table.update_item(
            Key={
                'photo_id': photo_id
            },
            AttributeUpdates={
                'labels': {
                    'Value': json.loads(json.dumps(rekognized_labels), parse_float=decimal.Decimal),
                    'Action': 'PUT'
                }
            }
        )

        return
    except Exception as e:
        logger.error('Unknown error occurred')

        raise e
