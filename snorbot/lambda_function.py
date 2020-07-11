import json
import logging
import os
import time

import boto3

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def format_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "X-Slack-No-Retry": 1,
            "Content-Type": "application/json"
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

    slack_event = body.get("event")
    user = slack_event.get("user")
    authed_users = body.get("authed_users", [])
    if user in authed_users:
        return format_response(200, {})

    event_time = int(body.get("event_time", 0)) + 10
    current_time = time.time()
    logger.info(f'Event Time: {event_time}, Current Time: {current_time}')
    if event_time > current_time:
        logger.info(f'passing event to destination: {event}')
        client = boto3.client("lambda")
        client.invoke(FunctionName="snorslack", Payload=event.get("body"))
    return format_response(200, {})
