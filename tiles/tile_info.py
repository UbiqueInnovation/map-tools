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

    @property
    @abstractmethod
    def bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        pass

    @property
    def top_left(self) -> tuple[float, float]:
        (left, top), _ = self.bounds
        return left, top

    @property
    def bottom_right(self) -> tuple[float, float]:
        _, (right, bottom) = self.bounds
        return right, bottom

    @property
    def min_coordinate(self) -> tuple[float, float]:
        (left, _), (_, bottom) = self.bounds
        return left, bottom

    @property
    def max_coordinate(self) -> tuple[float, float]:
        (_, top), (right, _) = self.bounds
        return right, top
