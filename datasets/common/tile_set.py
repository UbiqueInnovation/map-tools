from dataclasses import dataclass

from tiles import TileInfo


@dataclass(frozen=True)
class TileSet:
    path: str
    file_extension: str

    def tile_base_path(self, tile_info: TileInfo) -> str:
        return f"{self.path}/{tile_info.path}"

    def tile_path(self, tile_info: TileInfo) -> str:
        return f"{self.tile_base_path(tile_info)}.{self.file_extension}"
