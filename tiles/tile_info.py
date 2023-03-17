from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TileInfo:
    x: int
    y: int
    zoom: int

    def children(self) -> list[TileInfo]:
        x0, y0 = self.x * 2, self.y * 2
        zoom = self.zoom + 1
        return [
            TileInfo(x0, y0, zoom),
            TileInfo(x0, y0 + 1, zoom),
            TileInfo(x0 + 1, y0, zoom),
            TileInfo(x0 + 1, y0 + 1, zoom)
        ]
