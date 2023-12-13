from mypy_boto3_s3.service_resource import Bucket

from tiles import TileInfo
from . import TileOutput


class BucketTileOutput(TileOutput):
    def __init__(
        self,
        bucket: Bucket,
        base_path: str,
        acl: str = "public-read",
        cache_control: str = "max-age=86400",  # 1 day
    ) -> None:
        self.bucket = bucket
        self.base_path = base_path
        self.acl = acl
        self.cache_control = cache_control

    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        self.bucket.upload_file(
            file_path,
            f"{self.base_path}/{tile_info.path}.png",
            ExtraArgs={"ACL": self.acl, "CacheControl": self.cache_control},
        )
