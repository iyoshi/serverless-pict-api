import datetime
import json
import logging
import uuid

import jwt
from flask import Flask, jsonify, request
from pynamodb.exceptions import DoesNotExist, DeleteError, GetError, PutError, QueryError, UpdateError

from src.models.images import Images

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def validate_request_body(body):
    return body.keys() >= {'image_id', 'status'}


@app.route('/version', methods=['GET'])
def get_version():
    with open('../package.json', 'r') as f:
        pkg = json.loads(f.read())
        response_body = dict(version=pkg['version'])

        return jsonify(response_body), 200


@app.route('/images', methods=['POST'])
def post_images():
    auth_header = request.headers.get('Authorization', type=str)
    credentials = jwt.decode(auth_header, verify=False)
    user_id = credentials['sub']

    body = request.json

    image_id = str(uuid.uuid4())

    image = Images(image_id)
    image.user_id = user_id
    image.status = 'waiting'
    image.type = body.get('type')
    image.size = body.get('size')
    image.created_at = int(datetime.datetime.utcnow().timestamp())

    entity: Images = None
    try:
        image.save()
        entity = image.get(image_id)

    except (PutError, GetError) as err:

        return jsonify(err.msg), 500

    response_body = dict(image_id=entity.image_id, user_id=entity.user_id, status=entity.status, type=entity.type,
                         size=entity.size, created_at=entity.created_at, version=entity.version)

    return jsonify(response_body), 200


@app.route('/images', methods=['GET'])
def get_images():
    auth_header = request.headers.get('Authorization', type=str)
    credentials = jwt.decode(auth_header, verify=False)
    user_id = credentials['sub']

    try:
        images: [Images] = Images.user_id_index.query(
            user_id,
            limit=100,
            consistent_read=False,
            filter_condition=(Images.status == 'uploaded'))

    except QueryError as err:

        return jsonify(err.msg), 500

    try:
        items = [dict(image_id=e.image_id, status=e.status, type=e.type, size=e.size, created_at=e.created_at,
                      version=e.version) for e in images]
        response_body = dict(images=items)

        return jsonify(response_body), 200

    except Exception as err:
        logger.error('type: %s', type(err))
        logger.error(err)

        return jsonify('Unexpected error occurred'), 500


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id: str):
    if image_id is None:
        return jsonify('Required params is invalid'), 400

    image: Images = None
    try:
        image = Images.get(hash_key=image_id, consistent_read=True)

    except DoesNotExist as err:

        return jsonify(err.msg), 404

    except GetError as err:

        return jsonify(err.msg), 500

    try:
        response_body = dict(image_id=image.image_id, status=image.status, type=image.type, size=image.size,
                             created_at=image.created_at, version=image.version)

        return jsonify(response_body), 200

    except Exception as err:

        return jsonify('Unexpected error occurred'), 500


@app.route('/images', methods=['PUT'])
def update_image():
    body = request.json
    if not validate_request_body(body):
        logger.error("Validation Failed")

        return jsonify('Required params is invalid'), 400

    image_id = body.get('image_id')
    status = body.get('status')

    image: Images = None
    try:
        Images(image_id).update({'status': {'value': status, 'action': 'PUT'}})
        image = Images.get(image_id)

    except (UpdateError, GetError) as err:
        return jsonify(err.msg), 500

    try:
        response_body = dict(image_id=image.image_id, status=image.status, type=image.type, size=image.size,
                             created_at=image.created_at, version=image.version)

        return jsonify(response_body), 200

    except Exception as err:
        logger.error('type: %s', type(err))

        return jsonify('Unexpected error occurred'), 500


@app.route('/images/<image_id>', methods=['DELETE'])
def delete_image(image_id: str):
    if image_id is None:
        logger.error("Validation Failed")

        return jsonify('Required params is invalid'), 400

    try:
        image = Images.get(hash_key=image_id)
        image.delete()

    except DoesNotExist as err:

        return jsonify(err.msg), 404

    except DeleteError as err:

        return jsonify(err.msg), 500

    logger.info('photo_id = %s is successfully deleted.', image_id)

    return jsonify(dict(image_id=image_id)), 200
