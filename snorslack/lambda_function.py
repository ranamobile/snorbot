import json
import logging
import os
import random

from googletrans import Translator

import slackapi
import gphotoapi

PHOTO_RESPONSES = [
    "Whoaaaaaaaa coooooooolllll! :charmander-yay:",
    "OMG, that's amazing!! :mewtwo:",
    "Pika pika piiiiiiii!! :wooloo:",
    "Awwwwwwww :heart: :mankey-cute:",
    "我喜欢冰淇淋!! :hugging_face: :heart:",
    "我的猴子在哪里？ :mankey-cute: :snorlax_jason:",
]
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logging.info(f'received event info: {event}')
    if event.get("type") != "message":
        slackapi.format_response(200, {})

    slack_event = event.get("event")
    user = slack_event.get("user")
    channel = slack_event.get("channel")
    message = slack_event.get("text", "")
    authed_users = event.get("authed_users", [])

    if user in authed_users:
        return slackapi.format_response(200, {})

    # Translate message into English
    try:
        translator = Translator()
        language = translator.detect(message)
        if language.lang in ("zh-CN", "es", "ja", "fr", "ko"):
            translation = translator.translate(message)
            response = f'[Translated from {translation.src}] <@{user}>: {translation.text}'
            slackapi.post_message(channel, response)
    except Exception as error:
        logger.error(f'Failed to translate message: [{error}]')

    # Reply to posted photos
    if slack_event.get("subtype") == "file_share":
        response = random.choice(PHOTO_RESPONSES)
        slackapi.post_message(channel, response)
        logger.info(f'Response to file share: [{response}]')

        # Upload posted photos to Google Drive
        message_files = slack_event.get("files", [])
        for file_info in message_files:
            download_url = file_info.get("url_private_download")
            filename = file_info.get("name")
            filepath = slackapi.get_file_data(download_url)
            if filepath:
                channel_name = slackapi.get_channel_name(channel)
                image_id = gphotoapi.upload_image(channel_name, filename, filepath)
                logger.info(f'Uploaded [{filepath}] to [{channel_name}::{filename}]: [{image_id}]')

    return slackapi.format_response(200, {})
