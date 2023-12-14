import os

from dotenv import load_dotenv

from . import TileSet


class Dataset:
    def __init__(self, relative_path: str) -> None:
        self.path = f"{Dataset.parent_path()}/{relative_path}"
        self.base_path = os.path.dirname(self.path)

    @staticmethod
    def parent_path() -> str:
        load_dotenv()  # take environment variables from .env.
        return os.environ.get("DATA_PATH", "./data")

    def tile_set(self, name: str, file_extension: str) -> TileSet:
        return TileSet(f"{self.base_path}/{name}", file_extension)

    def resolve(self, relative_path: str) -> "Dataset":
        return Dataset(f"{self.base_path}/{relative_path}")

    @property
    def warped(self) -> TileSet:
        return self.tile_set("warped", "tif")

    @property
    def hillshade(self) -> TileSet:
        return self.tile_set("hillshade", "png")

    @property
    def color_relief(self) -> TileSet:
        return self.tile_set("color-relief", "png")

    def __str__(self) -> str:
        return self.__class__.__name__
