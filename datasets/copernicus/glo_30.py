from typing import Iterable
from urllib.request import urlopen

from datasets.common.downloadable_dataset import DownloadableDataset


class Glo30(DownloadableDataset):
    base_url = "https://copernicus-dem-30m.s3.amazonaws.com"

    def __init__(self) -> None:
        super().__init__("Glo30")

    @staticmethod
    def tile_names() -> list[str]:
        with urlopen(f"{Glo30.base_url}/tileList.txt") as tile_list:
            return [t.decode().strip() for t in tile_list.readlines()]

    @staticmethod
    def to_url(tile_name: str) -> str:
        return f"{Glo30.base_url}/{tile_name}/{tile_name}.tif"

    def get_urls(self) -> Iterable[str]:
        return [self.to_url(tile_name) for tile_name in self.tile_names()]
