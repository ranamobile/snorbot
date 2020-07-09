import json
import os
import urllib.request

from googletrans import Translator

SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_OAUTH_TOKEN = os.environ["SLACK_OAUTH_TOKEN"]
SLACK_API_CHAT_POSTMESSAGE = "https://slack.com/api/chat.postMessage"
SLACK_API_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f'Bearer {SLACK_OAUTH_TOKEN}',
}

translator = Translator()


def _format_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-type": "application/json"
        },
        "body": json.dumps(body),
    }


def _post_message(channel, message):
    payload = {
        "token": SLACK_OAUTH_TOKEN,
        "channel": channel,
        "text": message,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url=SLACK_API_CHAT_POSTMESSAGE, headers=SLACK_API_HEADERS,
                                     data=data, method="POST")
    with urllib.request.urlopen(request) as response:
        return response.status


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

    language = translator.detect(message)
    if language.lang in ("zh-CN", "es", "ja", "fr", "ko"):
        translation = translator.translate(message)
        response = f'[Translated from {translation.src}] <@{user}>: {translation.text}'
        _post_message(channel, response)

    return _format_response(200, {})
