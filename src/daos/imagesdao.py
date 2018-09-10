import datetime
import logging
from http import HTTPStatus
from typing import List, Optional

from pynamodb.exceptions import PutError, GetError, DoesNotExist, UpdateError, DeleteError, QueryError
from pynamodb.expressions.update import Action
from pynamodb.pagination import ResultIterator

from src.exceptions.apierror import ApiError
from src.models.images import Images

logger = logging.getLogger(__name__)


class ImagesDao:

    def __init__(self):
        pass

    def _handle_exception(self, ex) -> ApiError:
        code = ex.cause.response['Error'].get('Code')

        if code == 'ConditionalCheckFailedException':
            logger.warning('DynamoDB error occurred: %s', ex.msg)
            error_body = dict(code='conditional_check_failed',
                              message='A logical conflict to write request has occurred. Please try again later.')

            return ApiError(HTTPStatus.CONFLICT, error_body)

        if code == 'ProvisionedThroughputExceededException':
            logger.warning('DynamoDB error occurred: %s', ex.msg)
            error_body = dict(code='provisioned_throughput_exceeded',
                              message='DB provisioned throughput has exceeded. Please try again later.')

            return ApiError(HTTPStatus.CONFLICT, error_body)

        if code == 'ServiceUnavailable':
            logger.warning('DynamoDB error occurred: %s', ex.msg)
            error_body = dict(code='service_unavailable',
                              message='DB service unavailable now. Please try again later.')

            return ApiError(HTTPStatus.SERVICE_UNAVAILABLE, error_body)

        if code == 'InternalServerError':
            logger.warning('DynamoDB error occurred: %s', ex.msg)
            error_body = dict(code='internal_server_error',
                              message='Internal server error occurred at DB.')

            return ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, error_body)

        logger.error('DynamoDB error occurred: %s', ex.msg)
        error_body = dict(code='internal_server_error',
                          message='Unknown error occurred at DB.')

        return ApiError(HTTPStatus.INTERNAL_SERVER_ERROR, error_body)

    def create(self, item: Images) -> Images:

        current_time = int(datetime.datetime.utcnow().timestamp())
        item.created_at = current_time
        item.updated_at = current_time
        print(f'created updated_at value: {item.updated_at}')

        try:
            item.save()

            return Images.get(item.image_id, consistent_read=True)

        except (PutError, GetError) as e:
            raise self._handle_exception(e)

    def find(self, image_id: str) -> Optional[Images]:

        try:
            return Images.get(image_id, consistent_read=False)

        except DoesNotExist as e:
            return None

        except GetError as e:
            raise self._handle_exception(e)

    def find_all_with_user_id(self, user_id: str) -> ResultIterator:
        try:
            return Images.user_id_index.query(user_id, limit=100, consistent_read=False)

        except QueryError as e:
            raise self._handle_exception(e)

    def update(self, item: Images, actions: List[Action]) -> Images:
        try:
            actions.append(Images.updated_at.set(int(datetime.datetime.utcnow().timestamp())))
            item.update(actions=actions)

            return Images.get(item.image_id, consistent_read=True)

        except (UpdateError, GetError) as e:
            raise self._handle_exception(e)

    def delete(self, item: Images) -> Images:
        try:
            item.delete()

            return item

        except DeleteError as e:
            raise self._handle_exception(e)
