from typing import Iterable
from urllib.request import urlopen

from datasets.common.downloadable_dataset import DownloadableDataset


class SwissAlti3d(DownloadableDataset):
    def __init__(self, high_res: bool = False):
        super().__init__("SwissAlti3d/50cm" if high_res else "SwissAlti3d/2m")
        self.high_res = high_res

    def get_urls(self) -> Iterable[str]:
        tile_list_url_id = "CF5qMzKt" if self.high_res else "VsCRQHfw"
        url = (
            f"https://ogd.swisstopo.admin.ch/resources/"
            f"ch.swisstopo.swissalti3d-{tile_list_url_id}.csv"
        )
        with urlopen(url) as tile_list:
            return [t.decode().strip() for t in tile_list.readlines()]
