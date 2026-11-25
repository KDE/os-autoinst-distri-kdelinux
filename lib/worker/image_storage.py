# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

import os

import boto3
import botocore.exceptions
import requests
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

from lib.common.log import get_logger

logger = get_logger(__name__)

_S3_URL = "https://s3.kde.org"
_S3_BUCKET_NAME = "kde-linux-qa"

_MB = 1024 * 1024


class ImageStorage:
    def __init__(self) -> None:
        pass

    def _s3_connection(self):
        token_params = {"token": os.getenv("MINIO_OIDC")}
        r = requests.post("https://tokens.kde.org/minio/gitlab", data=token_params)
        credentials = r.json()

        try:
            s3_client = boto3.client(
                service_name="s3",
                endpoint_url=_S3_URL,
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
            )
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error getting s3 connection? {e}")
            raise

        return s3_client

    def upload_asset(
        self, local_file_path: str, object_key: str, metadata: dict | None = None
    ):
        s3_client = self._s3_connection()

        transfer_config = TransferConfig(multipart_chunksize=10 * _MB)
        extra_args = {"Metadata": metadata} if metadata else None

        try:
            s3_client.upload_file(
                Filename=local_file_path,
                Key=object_key,
                ExtraArgs=extra_args,
                Config=transfer_config,
                Bucket=_S3_BUCKET_NAME,
            )
        except (boto3.exceptions.S3UploadFailedError,botocore.exceptions.ClientError) as e:
            logger.error(f"Error getting s3 connection? {e}")
            raise

    def remove_asset(self, object_key: str) -> None:
        s3_client = self._s3_connection()

        try:
            s3_client.delete_object(Bucket=_S3_BUCKET_NAME, Key=object_key)
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error getting s3 connection? {e}")
            raise
