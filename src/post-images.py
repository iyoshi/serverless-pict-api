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

dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION'))
table = dynamodb.Table(os.getenv('PHOTOS_TABLE_NAME'))


def handler(event, context):

    body = json.loads(event['body'])
    credentials = jwt.decode(event.headers['Authorization'], verify=False)
    user_id = credentials.sub

    ext = body['type'].split('/')[1]
    photo_id = str(uuid.uuid4())
    url = get_pre_signed_url(
        os.getenv('PHOTOS_BUCKET'),
        photo_id + '.' + ext,
        body['type']
    )

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

    item['signed_url'] = url
    response = {
        'statusCode': 200,
        'body': json.dumps(item),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    return response


def get_pre_signed_url(bucket, key, type):
    s3 = boto3.client('s3', region_name=os.getenv('AWS_DEFAULT_REGION'))

    try:

        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': bucket, 'Key': key},
            HttpMethod='PUT',
            ExpiresIn=3600
        )

        return url

    except ClientError as e:
        raise e
