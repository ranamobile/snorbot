import json
import os
import random

import requests
from googletrans import Translator

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_OAUTH_TOKEN = os.environ["SLACK_OAUTH_TOKEN"]
SLACK_API_CHAT_POSTMESSAGE = "https://slack.com/api/chat.postMessage"
SLACK_API_CONVO_INFO = "https://slack.com/api/conversations.info"
SLACK_API_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f'Bearer {SLACK_OAUTH_TOKEN}',
}

PHOTO_RESPONSES = [
    "Whoaaaaaaaa coooooooolllll! :charmander-yay:",
    "OMG, that's amazing!! :mewtwo:",
    "Pika pika piiiiiiii!! :wooloo:",
    "Awwwwwwww :heart: :mankey-cute:",
    "我喜欢冰淇淋!! :hugging_face: :heart:",
    "我的猴子在哪里？ :mankey-cute: :snorlax_jason:",
]


def _format_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-type": "application/json"
        },
        "body": json.dumps(body),
    }


def _get_channel_name(channel):
    payload = {"channel": channel}
    response = requests.get(SLACK_API_CONVO_INFO, params=payload, headers=SLACK_API_HEADERS)
    metadata = response.json()
    return metadata["channel"]["name"]


def _post_message(channel, message):
    payload = {
        "token": SLACK_OAUTH_TOKEN,
        "channel": channel,
        "text": message,
    }
    data = json.dumps(payload)
    response = requests.post(SLACK_API_CHAT_POSTMESSAGE, headers=SLACK_API_HEADERS, data=data)
    return response.status_code


def lambda_handler(event, context):
    body = json.loads(event.get("body", ""))

    if body.get("token") != SLACK_VERIFICATION_TOKEN:
        return _format_response(400, {"error": "failed to authenticate slackbot"})

    if body.get("type") == "url_verification":
        return _format_response(200, {"challenge": body.get("challenge")})

    slack_event = body.get("event")
    user = slack_event.get("user")
    channel = slack_event.get("channel")
    message = slack_event.get("text", "")

    # Translate message into English
    translator = Translator()
    language = translator.detect(message)
    if language.lang in ("zh-CN", "es", "ja", "fr", "ko"):
        translation = translator.translate(message)
        response = f'[Translated from {translation.src}] <@{user}>: {translation.text}'
        _post_message(channel, response)

    # Reply to posted photos
    if slack_event.get("subtype") == "file_share":
        response = random.choice(PHOTO_RESPONSES)
        _post_message(channel, response)

    return _format_response(200, {})
