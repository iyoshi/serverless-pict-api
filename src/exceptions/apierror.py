from http import HTTPStatus

from src.models.errorbody import ErrorBody

class ApiError(Exception):

    def __init__(self, status_code: HTTPStatus, error_body: ErrorBody):
        self.__status_code = status_code
        self.__error_body = error_body

    @property
    def status_code(self):
        return self.__status_code

    @property
    def error_body(self):
        return self.__error_body
