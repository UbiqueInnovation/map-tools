from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from . import TileInfo, Wgs84Coordinate

top_left_coordinate = Wgs84Coordinate(lat=90, lon=-180)

coordinate_system_width = 360  # lon: [-180, 180]
coordinate_system_height = 180  # lat: [-90, 90]


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, order=True)
class Wgs84TileInfo(TileInfo):
    zoom: int
    x: int
    y: int

    @property
    def srs(self) -> str:
        return "EPSG:4326"

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
    def bounds(self) -> tuple[Wgs84Coordinate, Wgs84Coordinate]:
        tile_width, tile_height = self.size

        tile_left = top_left_coordinate.lon + self.x * tile_width
        tile_top = top_left_coordinate.lat - self.y * tile_height
        return (
            Wgs84Coordinate(lat=tile_top, lon=tile_left),
            Wgs84Coordinate(lat=tile_top - tile_height, lon=tile_left + tile_width),
        )

    @property
    def top_left(self) -> Wgs84Coordinate:
        top_left, _ = self.bounds
        return top_left

    @property
    def bottom_right(self) -> Wgs84Coordinate:
        _, bottom_right = self.bounds
        return bottom_right

    @property
    def min_coordinate(self) -> Wgs84Coordinate:
        a, b = self.bounds
        return Wgs84Coordinate(lat=min(a.lat, b.lat), lon=min(a.lon, b.lon))

    @property
    def max_coordinate(self) -> Wgs84Coordinate:
        a, b = self.bounds
        return Wgs84Coordinate(lat=max(a.lat, b.lat), lon=max(a.lon, b.lon))

    @property
    def children(self) -> set[Wgs84TileInfo]:
        x0, y0 = self.x * 2, self.y * 2
        zoom = self.zoom + 1
        return {
            Wgs84TileInfo(zoom=zoom, x=x0, y=y0),
            Wgs84TileInfo(zoom=zoom, x=x0, y=y0 + 1),
            Wgs84TileInfo(zoom=zoom, x=x0 + 1, y=y0),
            Wgs84TileInfo(zoom=zoom, x=x0 + 1, y=y0 + 1),
        }

    @property
    def parent(self) -> Wgs84TileInfo:
        return Wgs84TileInfo(zoom=self.zoom - 1, x=self.x // 2, y=self.y // 2)

    def descendants(self, max_zoom: int, min_zoom: int = 0) -> Iterable[Wgs84TileInfo]:
        if self.zoom > max_zoom:
            return []

        if self.zoom >= min_zoom:
            yield self

        for child in self.children:
            for descendant in child.descendants(min_zoom=min_zoom, max_zoom=max_zoom):
                yield descendant

    def ancestors(
        self, min_zoom: int = 0, max_zoom: int = 30
    ) -> Iterable[Wgs84TileInfo]:
        if self.zoom <= max_zoom:
            yield self

        if self.zoom > min_zoom:
            yield self.parent
            for ancestor in self.parent.ancestors(min_zoom, max_zoom):
                yield ancestor

    def overlapping(
        self, min_zoom: int = 0, max_zoom: int = 30
    ) -> Iterable[Wgs84TileInfo]:
        return set(self.ancestors(min_zoom=min_zoom, max_zoom=max_zoom)).union(
            self.descendants(min_zoom=min_zoom, max_zoom=max_zoom)
        )

    @staticmethod
    def within_bounds(
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        min_zoom: int = 0,
        max_zoom: int = 30,
    ) -> Iterable[Wgs84TileInfo]:
        def is_within_bounds(tile: Wgs84TileInfo) -> bool:
            return (
                min_lon <= tile.max_coordinate.lon
                and min_lat <= tile.max_coordinate.lat
                and max_lon >= tile.min_coordinate.lon
                and max_lat >= tile.min_coordinate.lat
            )

        return filter(
            is_within_bounds,
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(
                min_zoom=min_zoom, max_zoom=max_zoom
            ),
        )
