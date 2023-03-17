from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

max_value = 20_037_508.3427892
max_coordinate = max_value, max_value

min_value = -max_value
min_coordinate = min_value, max_value

coordinate_system_width = 2 * max_value
coordinate_system_height = coordinate_system_width


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, order=True)
class TileInfo:
    zoom: int
    x: int
    y: int

    @property
    def path(self) -> str:
        return f'{self.zoom}/{self.x}/{self.y}'

    @property
    def size(self) -> tuple[float, float]:
        num_tiles = 2 ** self.zoom
        tile_width = coordinate_system_width / num_tiles
        tile_height = coordinate_system_height / num_tiles
        return tile_width, tile_height

    @property
    def bounds(self) -> tuple[tuple[float, float], tuple[float, float]]:
        x0, _ = min_coordinate
        _, y0 = max_coordinate
        tile_width, tile_height = self.size

        tile_left = x0 + self.x * tile_width
        tile_top = y0 - self.y * tile_height
        return (tile_left, tile_top), (tile_left + tile_width, tile_top - tile_width)

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

    @property
    def children(self) -> set[TileInfo]:
        x0, y0 = self.x * 2, self.y * 2
        zoom = self.zoom + 1
        return {
            TileInfo(zoom=zoom, x=x0, y=y0),
            TileInfo(zoom=zoom, x=x0, y=y0 + 1),
            TileInfo(zoom=zoom, x=x0 + 1, y=y0),
            TileInfo(zoom=zoom, x=x0 + 1, y=y0 + 1)
        }

    def descendants(self, max_zoom: int) -> Iterable[TileInfo]:
        if self.zoom > max_zoom:
            return []

        yield self

        for child in self.children:
            for descendant in child.descendants(max_zoom):
                yield descendant
