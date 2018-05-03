import json
import logging
import os

import boto3
from botocore.client import ClientError

from src.decimalencoder import DecimalEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):
    """
    TBD.

    :param event: TBD
    :param context: TBD
    :return: TBD
    """

    path_params = event['pathParameters']

    if 'image_id' not in path_params:
        logger.error("Validation Failed")

        return {
            'statusCode': 400,
            'body': 'Required params is invalid',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    photo_id = path_params['image_id']
    dynamodb = boto3.resource('dynamodb',
                              region_name=os.getenv('AWS_DEFAULT_REGION'))
    table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME', 'photos'))
    try:
        result = table.get_item(Key={'photo_id': photo_id})

        if 'Item' not in result:
            return {
                'statusCode': 404,
                'body': 'Resource not found',
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

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

        item = result['Item']

        return {
            'statusCode': 200,
            'body': json.dumps(item, cls=DecimalEncoder),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as err:
        logger.error('type: %s', type(err))
        logger.error(err)

        return {
            'statusCode': 500,
            'body': 'Unexpected error occurred',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
