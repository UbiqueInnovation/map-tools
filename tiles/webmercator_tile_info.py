from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from . import TileInfo

max_value = 20_037_508.3427892
max_coordinate = max_value, max_value

min_value = -max_value
min_coordinate = min_value, max_value

coordinate_system_width = 2 * max_value
coordinate_system_height = coordinate_system_width


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, order=True)
class WebmercatorTileInfo(TileInfo):
    zoom: int
    x: int
    y: int

    @property
    def srs(self) -> str:
        return "EPSG:3857"

    @property
    def path(self) -> str:
        return f"{self.zoom}/{self.x}/{self.y}"

    @property
    def size(self) -> tuple[float, float]:
        num_tiles = 2**self.zoom
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
    def children(self) -> set[WebmercatorTileInfo]:
        x0, y0 = self.x * 2, self.y * 2
        zoom = self.zoom + 1
        return {
            WebmercatorTileInfo(zoom=zoom, x=x0, y=y0),
            WebmercatorTileInfo(zoom=zoom, x=x0, y=y0 + 1),
            WebmercatorTileInfo(zoom=zoom, x=x0 + 1, y=y0),
            WebmercatorTileInfo(zoom=zoom, x=x0 + 1, y=y0 + 1),
        }

    def descendants(self, max_zoom: int, min_zoom: int = 0) -> Iterable[TileInfo]:
        if self.zoom > max_zoom:
            return []

        if self.zoom >= min_zoom:
            yield self

        for child in self.children:
            for descendant in child.descendants(min_zoom=min_zoom, max_zoom=max_zoom):
                yield descendant
