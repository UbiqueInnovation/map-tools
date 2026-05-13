from typing import BinaryIO, override

from pmtiles.tile import zxy_to_tileid, TileType, Compression
from pmtiles.writer import Writer

from commons import TileOutput
from tiles import TileInfo


class PMTilesOutput(TileOutput):

    def __init__(self, file: BinaryIO, tile_type: TileType = TileType.WEBP) -> None:
        self.tile_type = tile_type
        self.writer = Writer(file)

    @override
    def save(self, file_path: str, tile_info: TileInfo) -> None:
        with open(file_path, "rb") as tile:
            self.save_bytes(tile.read(), tile_info)

    def save_bytes(self, data: bytes, tile_info: TileInfo) -> None:
        z, x, y = tile_info.zxy
        tile_id = zxy_to_tileid(z=z, x=x, y=y)
        self.writer.write_tile(tile_id, data)

    def finalize(self) -> None:
        self.writer.finalize(
            header={
                "tile_type": self.tile_type,
                "tile_compression": Compression.NONE,
                "min_zoom": 0,
                "max_zoom": 3,
                "min_lon_e7": int(-180.0 * 10000000),
                "min_lat_e7": int(-85.0 * 10000000),
                "max_lon_e7": int(180.0 * 10000000),
                "max_lat_e7": int(85.0 * 10000000),
                "center_zoom": 0,
                "center_lon_e7": 0,
                "center_lat_e7": 0,
            },
            metadata={},
        )
