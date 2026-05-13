import logging
import os
from typing import Optional

from mypy_boto3_s3.service_resource import Bucket

from . import Storage


class BucketStorage(Storage):

    def __init__(
        self,
        bucket: Bucket,
        acl: str = "public-read",
        content_type: str = "image/png",
        cache_control: str = "max-age=86400",  # 1 day
        content_encoding: Optional[str] = None,
    ) -> None:
        self.bucket = bucket
        self.acl = acl
        self.cache_control = cache_control
        self.content_type = content_type
        self.content_encoding = content_encoding

    def save(self, file_path: str, target_path: str) -> None:
        if os.stat(file_path).st_size == 0:
            logging.warning(f"File {file_path} is empty")

        extra_args = {
            "ACL": self.acl,
            "CacheControl": self.cache_control,
            "ContentType": self.content_type,
        }
        if self.content_encoding:
            extra_args["ContentEncoding"] = self.content_encoding

        self.bucket.upload_file(file_path, target_path, ExtraArgs=extra_args)
