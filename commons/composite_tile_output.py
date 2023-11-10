from typing import Iterable

from tiles import TileInfo
from . import TileOutput


class CompositeTileOutput(TileOutput):
    def __init__(self, tile_outputs: Iterable[TileOutput]) -> None:
        self.tile_outputs = list(tile_outputs)

    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        for tile_output in self.tile_outputs:
            tile_output.upload(file_path, tile_info)
