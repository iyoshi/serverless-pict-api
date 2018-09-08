import json
import logging
import uuid
from typing import List

import jwt
from flask import Flask, jsonify, request

from src.daos.imagesdao import ImagesDao
from src.exceptions.apierror import ApiError
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

    image_model = Images()
    image_model.image_id = str(uuid.uuid4())
    image_model.user_id = user_id
    image_model.status = 'waiting'
    image_model.type = body.get('type')
    image_model.size = body.get('size')

    images_dao = ImagesDao()
    try:
        created_model = images_dao.create(image_model)
        response_body = dict(image_id=created_model.image_id, status=created_model.status, tyoe=created_model.type,
                             size=created_model.size, created_at=created_model.created_at,
                             version=created_model.version)

        return jsonify(response_body), 200

    except ApiError as err:
        response_body = dict(code=err.error_body.code, message=err.error_body.message)
        return jsonify(response_body), int(err.status_code)

    except Exception as err:
        logger.error('Catching Internal Server Error', err)

        response_body = dict(code='internal_server_error', message=err.message)
        return jsonify(response_body), 500


@app.route('/images', methods=['GET'])
def get_images():
    auth_header = request.headers.get('Authorization', type=str)
    credentials = jwt.decode(auth_header, verify=False)
    user_id = credentials['sub']

    try:
        images: List[Images] = ImagesDao().find_all_with_user_id(user_id)
        filtered_images = [dict(image_id=image.image_id, status=image.status, type=image.type, size=image.size,
                                created_at=image.created_at,
                                version=image.version) for image in images if image.status == 'upload']

        response_body = dict(images=filtered_images)

        return jsonify(response_body), 200

    except ApiError as e:
        response_body = dict(code=e.error_body.code, message=e.error_body.message)
        return jsonify(response_body), int(e.status_code)


    except Exception as err:
        logger.error('Catching Internal Server Error', err)

        response_body = dict(code='internal_server_error', message=err.msg)
        return jsonify(response_body), 500


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id: str):
    if image_id is None:
        response_body = dict(code='invalid_parameter', message='"image_id" is required.')

        return jsonify(response_body), 400

    try:
        image = ImagesDao().find(image_id)

        if image is None:
            response_body = dict(code='resource_not_found', message='Images was not found.')
            return jsonify(response_body), 404

        response_body = {'image_id': image.image_id, 'status': image.status, 'type': image.type, 'size': image.size,
                         'created_at': image.created_at, 'version': image.version}

        return jsonify(response_body), 200

    except ApiError as e:
        response_body = dict(code=e.error_body.code, message=e.error_body.message)
        return jsonify(response_body), int(e.status_code)

    except Exception as err:
        app.logger.error('Catching Internal Server Error', str(err))

        response_body = {'code': 'internal_server_error', 'message': str(err)}
        return jsonify(response_body), 500


@app.route('/images', methods=['PUT'])
def update_image():
    body = request.json
    if not validate_request_body(body):
        response_body = dict(code='invalid_parameter', message='Request body is invalid.')

        return jsonify(response_body), 400

    image_id = body.get('image_id')
    status = body.get('status')

    dao = ImagesDao()
    try:
        image = dao.find(image_id)
        actions = [image.status.set(status)]
        updated_image = dao.update(image, actions)

        response_body = dict(image_id=updated_image.image_id, status=updated_image.status, type=updated_image.type,
                             size=updated_image.size,
                             created_at=updated_image.created_at, version=updated_image.version)

        return jsonify(response_body), 200

    except ApiError as err:
        response_body = dict(code=err.error_body.code, message=err.error_body.message)
        return jsonify(response_body), int(err.status_code)

    except Exception as err:
        logger.error('Catching Internal Server Error', err)

        response_body = dict(code='internal_server_error', message=err.msg)
        return jsonify(response_body), 500


@app.route('/images/<image_id>', methods=['DELETE'])
def delete_image(image_id: str):
    if image_id is None:
        response_body = dict(code='invalid_parameter', message='"image_id" is required.')

        return jsonify(response_body), 400

    try:
        dao = ImagesDao()
        image = dao.find(image_id)

        if image is None:
            response_body = dict(code='resource_not_found', message='Images was not found.')
            return jsonify(response_body), 404

        dao.delete(image)

        return jsonify(dict(image_id=image_id)), 200

    except ApiError as err:
        response_body = dict(code=err.error_body.code, message=err.error_body.message)
        return jsonify(response_body), int(err.status_code)

    except Exception as err:
        logger.error('Catching Internal Server Error', err)

        response_body = dict(code='internal_server_error', message=err.msg)
        return jsonify(response_body), 500
