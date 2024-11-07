from typing import Optional, IO

from mypy_boto3_s3.service_resource import Bucket

from . import TileOutput


class BucketOutput(TileOutput):
    def __init__(
        self,
        bucket: Bucket,
        acl: str = "public-read",
        cache_control: str = "max-age=86400",  # 1 day
        content_type: str = "application/json",
        content_encoding: Optional[str] = None,
    ) -> None:
        self.bucket = bucket
        self.acl = acl
        self.cache_control = cache_control
        self.content_encoding = content_encoding
        self.content_type = content_type

    def upload(self, content: IO, target_path: str) -> None:
        extra_args = {
            "ACL": self.acl,
            "CacheControl": self.cache_control,
            "ContentType": self.content_type,
        }
        if self.content_encoding:
            extra_args["ContentEncoding"] = self.content_encoding

        self.bucket.upload_fileobj(content, target_path, ExtraArgs=extra_args)
