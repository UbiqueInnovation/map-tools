from abc import abstractmethod
from typing import Iterable

from ..source import Source


class SwissAlti3dSource(Source):

    @property
    @abstractmethod
    def tile_list(self) -> str:
        pass

    def get_urls(self) -> Iterable[str]:
        with open(f"sources/swissalti3d/{self.tile_list}") as tile_list:
            return [t.strip() for t in tile_list.readlines()]
