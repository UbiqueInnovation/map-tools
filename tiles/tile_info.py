from __future__ import annotations

from abc import abstractmethod, ABC


class TileInfo(ABC):

    @property
    def srs(self) -> str:
        return f"EPSG:{self.srid}"

    @property
    @abstractmethod
    def zxy(self) -> tuple[int, int, int]:
        pass

    @property
    @abstractmethod
    def srid(self) -> int:
        pass

    @property
    @abstractmethod
    def path(self) -> str:
        pass

    @property
    @abstractmethod
    def bounds_min_x_min_y_max_x_max_y(self) -> tuple[float, float, float, float]:
        pass
