#!/bin/python3

import argparse
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import io


def update_file(token, filename, fileID):
    creds, _ = google.auth.load_credentials_from_file(token)

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": filename}
        media = MediaFileUpload(filename)
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .update(body=file_metadata, media_body=media, fields="id", fileId=fileID)
            .execute()
        )
        print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.get("id")


def download_file(token, fileID):
    creds, _ = google.auth.load_credentials_from_file(token)

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=fileID)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.getbuffer()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A tool to handle file in google drive",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subcommand = parser.add_subparsers(dest="subcommand", help="subcommands")

    parser_update = subcommand.add_parser("update", help="update file in google dirver")

    parser_download = subcommand.add_parser(
        "download", help="download file from google dirver"
    )

    parser.add_argument(
        "--file_id",
        dest="file_id",
        type=str,
        action="store",
        help="file ID in google driver",
    )
    parser.add_argument("--token", type=str)
    parser.add_argument("--filename", dest="filename", type=str, action="store")

    args = parser.parse_args()

    if args.subcommand == "update":
        update_file(
            token=args.token,
            filename=args.filename,
            fileID=args.file_id,
        )
    elif args.subcommand == "download":
        with open(args.filename, "wb") as f:
            f.write(download_file(token=args.token, fileID=args.file_id))
