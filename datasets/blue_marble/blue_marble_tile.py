from dataclasses import dataclass

from tiles import Wgs84Coordinate


@dataclass(frozen=True, kw_only=True)
class BlueMarbleTile:
    col: str
    row: int
    upper_left: Wgs84Coordinate
    lower_right: Wgs84Coordinate

    @property
    def identifier(self) -> str:
        return f"{self.col}{self.row}"
