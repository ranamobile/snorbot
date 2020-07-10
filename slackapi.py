import json
import os

import requests

SLACK_OAUTH_TOKEN = os.environ["SLACK_OAUTH_TOKEN"]
SLACK_API_CHAT_POSTMESSAGE = "https://slack.com/api/chat.postMessage"
SLACK_API_CONVO_INFO = "https://slack.com/api/conversations.info"
SLACK_API_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f'Bearer {SLACK_OAUTH_TOKEN}',
}


def get_channel_name(channel):
    payload = {"channel": channel}
    response = requests.get(SLACK_API_CONVO_INFO, headers=SLACK_API_HEADERS, params=payload)
    metadata = response.json()
    return metadata["channel"]["name"]


def post_message(channel, message):
    payload = {
        "channel": channel,
        "text": message,
    }
    data = json.dumps(payload)
    response = requests.post(SLACK_API_CHAT_POSTMESSAGE, headers=SLACK_API_HEADERS, data=data)
    return response.status_code


def format_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-type": "application/json"
        },
        "body": json.dumps(body),
    }
