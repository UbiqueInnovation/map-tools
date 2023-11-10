from abc import abstractmethod

from tiles import TileInfo


class TileOutput:
    @abstractmethod
    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        pass
