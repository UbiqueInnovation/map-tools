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

    @property
    def parent(self) -> WebmercatorTileInfo:
        return WebmercatorTileInfo(zoom=self.zoom - 1, x=self.x // 2, y=self.y // 2)

    def descendants(self, max_zoom: int, min_zoom: int = 0) -> Iterable[TileInfo]:
        if self.zoom > max_zoom:
            return []

        if self.zoom >= min_zoom:
            yield self

        for child in self.children:
            for descendant in child.descendants(min_zoom=min_zoom, max_zoom=max_zoom):
                yield descendant

    def ancestors(self, min_zoom: int = 0, max_zoom: int = 30) -> Iterable[TileInfo]:
        if self.zoom <= max_zoom:
            yield self

        if self.zoom > min_zoom:
            yield self.parent
            for ancestor in self.parent.ancestors(min_zoom, max_zoom):
                yield ancestor

    def overlapping(self, min_zoom: int = 0, max_zoom: int = 30) -> Iterable[TileInfo]:
        return set(self.ancestors(min_zoom=min_zoom, max_zoom=max_zoom)).union(
            self.descendants(min_zoom=min_zoom, max_zoom=max_zoom)
        )

    @staticmethod
    def within_bounds(
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
        min_zoom: int = 0,
        max_zoom: int = 30,
    ) -> Iterable[TileInfo]:
        def is_within_bounds(tile: TileInfo) -> bool:
            t_min_x, t_min_y = tile.min_coordinate
            t_max_x, t_max_y = tile.max_coordinate
            return (
                min_x <= t_max_x
                and min_y <= t_max_y
                and max_x >= t_min_x
                and max_y >= t_min_y
            )

        return filter(
            is_within_bounds,
            WebmercatorTileInfo(zoom=0, x=0, y=0).descendants(
                min_zoom=min_zoom, max_zoom=max_zoom
            ),
        )
