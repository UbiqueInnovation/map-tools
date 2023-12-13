from typing import Iterable
from urllib.request import urlopen

from ..elevation_layer import ElevationLayer


class SwissAlti3d(ElevationLayer):
    def __init__(self, high_res: bool = False):
        super().__init__()
        self.high_res = high_res

    @property
    def tile_list_url_id(self) -> str:
        return "CF5qMzKt" if self.high_res else "VsCRQHfw"

    @property
    def local_path(self) -> str:
        return "SwissAlti3d/50cm" if self.high_res else "SwissAlti3d/2m"

    def get_urls(self) -> Iterable[str]:
        url = (
            f"https://ogd.swisstopo.admin.ch/resources/"
            f"ch.swisstopo.swissalti3d-{self.tile_list_url_id}.csv"
        )
        with urlopen(url) as tile_list:
            return [t.decode().strip() for t in tile_list.readlines()]
