import json

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_OAUTH_TOKEN = os.environ["SLACK_OAUTH_TOKEN"]


def _format_message(status, body):
    return {
        'statusCode': status,
        'headers': {
            'Content-type': 'application/json'
        },
        'body': json.dumps(body),
    }


def lambda_handler(event, context):
    body = json.loads(event.get('body', ''))

    if body.get('token') != SLACK_VERIFICATION_TOKEN:
        return _format_message(400, {'error': 'failed to authenticate slackbot'})

    if body.get('type') == 'url_verification':
        return _format_message(200, {'challenge': body.get('challenge')})

    else:
        if 'snorbot help' in body.get('text').lower():
            pass
