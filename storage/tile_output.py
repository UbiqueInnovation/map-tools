from tiles import TileInfo
from .r2_client import Bucket


class TileOutput:

    def __init__(self, bucket: Bucket, base_path: str) -> None:
        self.bucket = bucket
        self.base_path = base_path

    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        self.bucket.upload_file(file_path, f'{self.base_path}/{tile_info.path}.png')
