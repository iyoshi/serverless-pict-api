import boto3


class DynamoDbTestingUtil:

    __dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    def createDynamoDb(self):

        return self.__dynamodb