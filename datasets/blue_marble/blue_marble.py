import logging
import os
from typing import Iterable

from osgeo.gdal import Translate, TranslateOptions, BuildVRT, BuildVRTOptions

from datasets.common.downloadable_dataset import DownloadableDataset
from tiles import Wgs84Coordinate
from . import BlueMarbleTile


class BlueMarble(DownloadableDataset):
    base_url = "https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73801"
    date = "200409"
    resolution = "3x21600x21600"

    def __init__(self, layer: str = "world.topo.bathy") -> None:
        super().__init__(f"BlueMarble/{layer}")
        self.layer = layer

    @staticmethod
    def tiles() -> list[BlueMarbleTile]:
        return [
            BlueMarbleTile(
                row=row,
                col=col,
                upper_left=Wgs84Coordinate(lat=90 - i * 90, lon=j * 90 - 180),
                lower_right=Wgs84Coordinate(lat=-i * 90, lon=j * 90 - 90),
            )
            for i, row in enumerate([1, 2])
            for j, col in enumerate("ABCD")
        ]

    @staticmethod
    def tile_names() -> list[str]:
        return [tile.identifier for tile in BlueMarble.tiles()]

    def file_name(self, tile: BlueMarbleTile) -> str:
        return f"{self.layer}.{self.date}.{self.resolution}.{tile.identifier}"

    def to_url(self, tile: BlueMarbleTile) -> str:
        return f"{self.base_url}/{self.file_name(tile)}.png"

    def get_urls(self) -> Iterable[str]:
        return [self.to_url(tile) for tile in self.tiles()]

    def add_geo_reference(self) -> None:
        for tile in self.tiles():
            geo_tif_path = self.geo_tif_path(tile)
            if os.path.exists(geo_tif_path):
                logging.info(f"Geo referenced file already exists, skipping {tile}.")
                continue
            logging.info(f"Adding geo reference for {tile}.")
            Translate(
                srcDS=self.png_path(tile),
                destName=geo_tif_path,
                options=TranslateOptions(
                    outputSRS=Wgs84Coordinate.srs(),
                    outputBounds=[
                        tile.upper_left.x,
                        tile.upper_left.y,
                        tile.lower_right.x,
                        tile.lower_right.y,
                    ],
                    creationOptions=dict(COMPRESS="LZW", TILED=True),
                ),
            )

    def create_vrt(self) -> None:
        logging.info("Creating virtual data set")
        files = [self.geo_tif_path(tile) for tile in self.tiles()]
        BuildVRT(
            destName=self.path,
            srcDSOrSrcDSTab=files,
            options=BuildVRTOptions(),
        )

    def geo_tif_path(self, tile: BlueMarbleTile) -> str:
        return f"{self.data_path}/{self.file_name(tile)}.tif"

    def png_path(self, tile: BlueMarbleTile) -> str:
        return f"{self.data_path}/{self.file_name(tile)}.png"
