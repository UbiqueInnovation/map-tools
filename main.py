import logging

from osgeo import gdal

from commons import R2Client, TileOutput
from elevation import ElevationSwitzerland
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()
    layer = ElevationSwitzerland()
    tiles = list(WebmercatorTileInfo(zoom=6, x=33, y=22).descendants(max_zoom=14))

    layer.generate_color_relief_tiles(
        tiles,
        color_filename="elevation/relief-colors/hypsometric-tint-v3",
        output=TileOutput(r2_client.maps_dev, "tiles/v1/hypsometric-tint-v3"),
    )

    layer.generate_hillshade_tiles(
        tiles,
        options=gdal.DEMProcessingOptions(igor=True, zFactor=1.7, computeEdges=True),
        output=TileOutput(r2_client.maps_dev, "tiles/v1/hillshade/igor-1_7"),
    )
