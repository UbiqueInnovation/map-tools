import json
from typing import Iterable
from urllib.parse import quote_plus
from urllib.request import urlopen

from datasets.common.downloadable_dataset import DownloadableDataset


class SwissAlti3d(DownloadableDataset):
    def __init__(self, high_res: bool = False):
        super().__init__("SwissAlti3d/50cm" if high_res else "SwissAlti3d/2m")
        self.high_res = high_res

    def get_urls(self) -> Iterable[str]:
        search_dataset_url = (
            "https://ogd.swisstopo.admin.ch/services/swiseld/services/assets/"
            + "ch.swisstopo.swissalti3d/search"
            + "?format="
            + quote_plus("image/tiff; application=geotiff; profile=cloud-optimized")
            + "&resolution="
            + ("0.5" if self.high_res else "2.0")
            + "&srid=2056"
            + "&state=current"
            + "&csv=true"
        )
        with urlopen(search_dataset_url) as response:
            dataset_url = json.loads(response.read())["href"]

        with urlopen(dataset_url) as tile_list:
            return [t.decode().strip() for t in tile_list.readlines()]
