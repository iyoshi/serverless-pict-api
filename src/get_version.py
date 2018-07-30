import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event, context):

    with open('../package.json', 'r') as f:
        pkg = json.loads(f.read())
        response_body = dict(version=pkg['version'])

        return dict(
            statusCode=200,
            body=json.dumps(response_body),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            })
