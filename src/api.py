import json
import logging
import sys
import uuid
from http import HTTPStatus
from typing import List

import jwt
from flask import Flask, jsonify, request

from src.daos.imagesdao import ImagesDao
from src.exceptions.apierror import ApiError
from src.models.errorbody import ErrorBody
from src.models.images import Images

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_request_body(body):
    return body.keys() >= {'image_id', 'status'}

@app.errorhandler(ApiError)
def handle_error(error: ApiError):


    api_error_response = jsonify(dict(code=error.error_body.code, message=error.error_body.message))
    logger.warning('Error response: %s', error.error_body.message)

    return api_error_response, int(error.status_code)


@app.errorhandler(Exception)
def handle_unexpected_error(error: Exception):

    traceback = sys.exc_info()[2]
    error_message = error.with_traceback(traceback)
    unexpected_error_response = jsonify(dict(code='unexpected_error', message=error_message))

    logger.error('Error response: %s', error_message)

    return unexpected_error_response, int(HTTPStatus.INTERNAL_SERVER_ERROR)


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
    created_model = images_dao.create(image_model)
    response_body = dict(image_id=created_model.image_id, status=created_model.status, tyoe=created_model.type,
                         size=created_model.size, created_at=created_model.created_at,
                         version=created_model.version)

    return jsonify(response_body), 200

@app.route('/images', methods=['GET'])
def get_images():
    auth_header = request.headers.get('Authorization', type=str)
    credentials = jwt.decode(auth_header, verify=False)
    user_id = credentials['sub']

    images: List[Images] = ImagesDao().find_all_with_user_id(user_id)
    filtered_images = [dict(image_id=image.image_id, status=image.status, type=image.type, size=image.size,
                            created_at=image.created_at,
                            version=image.version) for image in images if image.status == 'upload']

    response_body = dict(images=filtered_images)

    return jsonify(response_body), 200

@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id: str):
    if image_id is None:
        raise ApiError(
            HTTPStatus.BAD_REQUEST,
            ErrorBody(code='invalid_parameter', message='"image_id" is required.')
        )

    image = ImagesDao().find(image_id)

    if image is None:
        raise ApiError(
            HTTPStatus.NOT_FOUND,
            ErrorBody(code='resource_not_found', message='Images was not found.')
        )

    response_body = {'image_id': image.image_id, 'status': image.status, 'type': image.type, 'size': image.size,
                     'created_at': image.created_at, 'version': image.version}

    return jsonify(response_body), 200

@app.route('/images', methods=['PUT'])
def update_image():
    body = request.json
    if not validate_request_body(body):
        raise ApiError(
            HTTPStatus.BAD_REQUEST,
            ErrorBody(code='invalid_parameter', message='Request body is invalid.')
        )

    image_id = body.get('image_id')
    status = body.get('status')

    dao = ImagesDao()
    image = dao.find(image_id)
    actions = [Images.status.set(status)]
    updated_image = dao.update(image, actions)

    response_body = dict(image_id=updated_image.image_id, status=updated_image.status, type=updated_image.type,
                         size=updated_image.size,
                         created_at=updated_image.created_at, version=updated_image.version)

    return jsonify(response_body), 200

@app.route('/images/<image_id>', methods=['DELETE'])
def delete_image(image_id: str):
    if image_id is None:

        raise ApiError(
            HTTPStatus.BAD_REQUEST,
            ErrorBody(code='invalid_parameter', message='"image_id" is required.')
        )

    dao = ImagesDao()
    image = dao.find(image_id)

    if image is None:

        raise ApiError(
            HTTPStatus.NOT_FOUND,
            ErrorBody(code='resource_not_found', message='Images was not found.'))

    dao.delete(image)

    return jsonify(dict(image_id=image_id)), 200
