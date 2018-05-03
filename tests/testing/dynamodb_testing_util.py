import boto3


class DynamoDbTestingUtil:

    @staticmethod
    def create_dynamodb_local_resource():

        return boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

    @staticmethod
    def delete_table(table_name):

        boto3.client('dynamodb', endpoint_url='http://localhost:8000').delete_table(
            TableName=table_name
        )
