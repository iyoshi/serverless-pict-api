import json
import os

import boto3
from botocore.client import ClientError
import logging

from src.decimalencoder import DecimalEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION'))
table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME'))

def validate_request_body(body):

    return body.keys() >= { 'photo_id', 'created_at', 'status' }


def handler(event, context):
    """
    TBD.

    :param event: TBD
    :param context: TBD
    :return: TBD
    """

    body = json.loads(event['body'])
    if not validate_request_body(body):

        logger.error("Validation Failed")

        return {
            'statusCode': 400,
            'body': 'Required params is invalid',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': "*"
            }
        }

    photo_id = body['photo_id']
    status = body['status']

    try:
        table.update_item(
            Key={
                'photo_id': photo_id
            },
            AttributeUpdates={
                'status': {
                    'Value': status,
                    'Action': 'PUT'
                }
            }
        )

        result = table.get_item(
            Key={
                'photo_id': photo_id
            }
        )

    except ClientError as err:
        logger.error(err.response['Error']['Code'])

        return {
            'statusCode': 500,
            'body': err.response['Error']['Code'],
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    try:
        response_body = json.dumps(result['Item'], cls=DecimalEncoder)

        return {
            'statusCode': 200,
            'body': response_body,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as err:
        logger.error('type: {}'.format(type(err)))

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
