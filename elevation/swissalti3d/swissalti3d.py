from abc import abstractmethod
from typing import Iterable

from ..elevation_layer import ElevationLayer


class SwissAlti3d(ElevationLayer):

    @property
    @abstractmethod
    def tile_list(self) -> str:
        pass

    def get_urls(self) -> Iterable[str]:
        with open(f"elevation/swissalti3d/{self.tile_list}") as tile_list:
            return [t.strip() for t in tile_list.readlines()]
