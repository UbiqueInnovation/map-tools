import logging

from osgeo import gdal

from commons import R2Client
from elevation import ElevationSwitzerland
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()

    layer = ElevationSwitzerland()
    swiss_tile_info = WebmercatorTileInfo(zoom=6, x=33, y=22)
    tiles = list(swiss_tile_info.overlapping(max_zoom=14))

    layer.generate_hillshade_tiles(
        tiles,
        options=gdal.DEMProcessingOptions(zFactor=1.7, computeEdges=True, igor=True),
    )

    layer.generate_color_relief_tiles(
        tiles,
        color_filename="elevation/relief-colors/hypsometric-tint",
    )
