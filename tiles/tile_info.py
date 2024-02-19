from __future__ import annotations

from abc import abstractmethod


class TileInfo:
    @property
    @abstractmethod
    def srs(self) -> str:
        pass

    @property
    @abstractmethod
    def path(self) -> str:
        pass
