import json
import logging
import os

import boto3

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def format_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-type": "application/json"
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    logger.info(f'received event from slack: {event}')
    body = json.loads(event.get("body", ""))

    if body.get("token") != SLACK_VERIFICATION_TOKEN:
        logger.error("token doesn't match slack")
        return format_response(400, {"error": "failed to authenticate slackbot"})

    if body.get("type") == "url_verification":
        logger.info("verified url")
        return format_response(200, {"challenge": body.get("challenge")})

    logger.info(f'passing event to destination: {event}')
    client = boto3.client("lambda")
    client.invoke(FunctionName="snorslack", Payload=event.get("body"))
    return format_response(200, {})
