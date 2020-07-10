import json
import os
import random

from googletrans import Translator

import slackapi

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
PHOTO_RESPONSES = [
    "Whoaaaaaaaa coooooooolllll! :charmander-yay:",
    "OMG, that's amazing!! :mewtwo:",
    "Pika pika piiiiiiii!! :wooloo:",
    "Awwwwwwww :heart: :mankey-cute:",
    "我喜欢冰淇淋!! :hugging_face: :heart:",
    "我的猴子在哪里？ :mankey-cute: :snorlax_jason:",
]


def lambda_handler(event, context):
    body = json.loads(event.get("body", ""))

    if body.get("token") != SLACK_VERIFICATION_TOKEN:
        return slackapi.format_response(400, {"error": "failed to authenticate slackbot"})

    if body.get("type") == "url_verification":
        return slackapi.format_response(200, {"challenge": body.get("challenge")})

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
        slackapi.post_message(channel, response)

    # Reply to posted photos
    if slack_event.get("subtype") == "file_share":
        response = random.choice(PHOTO_RESPONSES)
        slackapi.post_message(channel, response)

    return slackapi.format_response(200, {})
