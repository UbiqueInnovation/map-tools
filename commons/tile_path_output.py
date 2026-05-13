from typing import Literal

from tiles import TileInfo
from . import TileOutput, Storage


class TilePathOutput(TileOutput):
    def __init__(
        self,
        storage: Storage,
        base_path: str,
        tile_format: Literal["webp", "jpg", "png"] = "png",
    ) -> None:
        self.storage = storage
        self.base_path = base_path
        self.file_ending = tile_format
        self.content_type = f"image/{tile_format}"

    def save(self, file_path: str, tile_info: TileInfo) -> None:
        target_path = f"{self.base_path}/{tile_info.path}.{self.file_ending}"
        self.storage.save(file_path, target_path, content_type=self.content_type)
