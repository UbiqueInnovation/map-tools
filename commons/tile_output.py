from abc import abstractmethod, ABC

from tiles import TileInfo


class TileOutput(ABC):

    @abstractmethod
    def save(self, file_path: str, tile_info: TileInfo) -> None:
        pass
