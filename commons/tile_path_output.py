from tiles import TileInfo
from . import TileOutput, Storage


class TilePathOutput(TileOutput):
    def __init__(
        self,
        storage: Storage,
        base_path: str,
        file_ending: str = "png",
    ) -> None:
        self.storage = storage
        self.base_path = base_path
        self.file_ending = file_ending

    def save(self, file_path: str, tile_info: TileInfo) -> None:
        target_path = f"{self.base_path}/{tile_info.path}.{self.file_ending}"
        self.storage.save(file_path, target_path)
