from typing import Optional

from mypy_boto3_s3.service_resource import Bucket

from tiles import TileInfo
from . import TileOutput


class BucketTileOutput(TileOutput):
    def __init__(
        self,
        bucket: Bucket,
        base_path: str,
        file_ending: str = "png",
        acl: str = "public-read",
        cache_control: str = "max-age=86400",  # 1 day
        content_encoding: Optional[str] = None,
    ) -> None:
        self.bucket = bucket
        self.base_path = base_path
        self.file_ending = file_ending
        self.acl = acl
        self.cache_control = cache_control
        self.content_encoding = content_encoding

    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        extra_args = {
            "ACL": self.acl,
            "CacheControl": self.cache_control,
        }
        if self.content_encoding:
            extra_args["ContentEncoding"] = self.content_encoding

        self.bucket.upload_file(
            file_path,
            f"{self.base_path}/{tile_info.path}.{self.file_ending}",
            ExtraArgs=extra_args,
        )
