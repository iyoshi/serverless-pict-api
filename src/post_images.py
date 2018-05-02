import datetime
import json
import logging
import os
import uuid

import boto3
from botocore.client import ClientError
import jwt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb',
                          region_name=os.getenv('AWS_DEFAULT_REGION'))
table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME'))


def handler(event, context):

    body = json.loads(event['body'])
    credentials = jwt.decode(event.headers['Authorization'], verify=False)
    user_id = credentials.sub

    photo_id = str(uuid.uuid4())

    item = {
        'photo_id': photo_id,
        'user_id': user_id,
        'created_at': int(datetime.datetime.utcnow().timestamp()),
        'status': 'waiting',
        'type': body['type'],
        'size': body['size'],
        'version': 1
    }

    try:
        table.put_item(Item=item)

    except ClientError as err:
        logger.error(err.response['Error']['Code'])

        response = {
            'statusCode': 400,
            'body': err.response['Error']['Code'],
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

        return response

    response = {
        'statusCode': 200,
        'body': json.dumps(item),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    return response
