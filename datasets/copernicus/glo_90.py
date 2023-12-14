from typing import Iterable
from urllib.request import urlopen

from datasets.common.downloadable_dataset import DownloadableDataset


class Glo90(DownloadableDataset):
    base_url = "https://copernicus-dem-90m.s3.amazonaws.com"

    def __init__(self) -> None:
        super().__init__("Glo90")

    @staticmethod
    def tile_names() -> list[str]:
        with urlopen(f"{Glo90.base_url}/tileList.txt") as tile_list:
            return [t.decode().strip() for t in tile_list.readlines()]

    @staticmethod
    def to_url(tile_name: str) -> str:
        return f"{Glo90.base_url}/{tile_name}/{tile_name}.tif"

    def get_urls(self) -> Iterable[str]:
        return [self.to_url(tile_name) for tile_name in self.tile_names()]
