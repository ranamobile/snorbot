"""
References:
* http://googleapis.github.io/google-api-python-client
* https://developers.google.com/drive/api/v3/about-sdk
"""
import os

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
SERVICE_CREDS = os.path.join(BOT_DIRECTORY, "pikaservice_credentials.json")
MY_EMAIL_ADDRESS = "aunkei.hong@gmail.com"


credentials = service_account.Credentials.from_service_account_file(SERVICE_CREDS)
service = build("drive", "v3", credentials=credentials, cache_discovery=False)


def get_info():
    return service.about().get(fields="user,storageQuota").execute()


def create_directory(new_directory):
    response = service.files().list(
        q="mimeType='application/vnd.google-apps.folder'",
        spaces="drive", fields="nextPageToken,files(id, name)").execute()

    for directory in response.get("files", []):
        directory_name = directory.get("name")
        directory_id = directory.get("id")
        if directory_name == new_directory:
            share_file(directory_id)
            return directory_id

    metadata = {
        "name": new_directory,
        "mimeType": "application/vnd.google-apps.folder",
    }
    directory = service.files().create(body=metadata, fields="id").execute()
    directory_id = directory.get("id")
    share_file(directory_id)
    return directory_id


def delete_file(fileid):
    service.files().delete(fileId=fileid).execute()


def list_files():
    response = service.files().list(fields="nextPageToken,files(id, name)").execute()
    for file_obj in response.get("files", []):
        filename = file_obj.get("name")
        fileid = file_obj.get("id")
        yield filename, fileid


def share_file(file_id):
    metadata = {
        "type": "user",
        "role": "writer",
        "emailAddress": MY_EMAIL_ADDRESS,
    }
    service.permissions().create(fileId=file_id, body=metadata, fields='id').execute()


def upload_image(directory, image_name, image_path):
    directory_id = create_directory(directory)
    metadata = {
        "name": image_name,
        "parents": [directory_id],
    }
    media = MediaFileUpload(image_path)
    image = service.files().create(body=metadata, media_body=media, fields="id").execute()
    return image.get("id")
