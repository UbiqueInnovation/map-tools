from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True, unsafe_hash=True, order=True)
class Wgs84Coordinate:
    lat: float
    lon: float

    @staticmethod
    def srs() -> str:
        return "EPSG:4326"

    @property
    def x(self) -> float:
        return self.lon

    @property
    def y(self) -> float:
        return self.lat
