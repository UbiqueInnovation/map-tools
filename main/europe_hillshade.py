import logging

from osgeo import gdal

from commons import R2Client, TileOutput
from elevation import Glo90
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()

    layer = Glo90()

    for level in range(0, 11):
        tiles = list(
            WebmercatorTileInfo.within_bounds(
                min_x=-2_500_000,
                min_y=2_500_000,
                max_x=5_000_000,
                max_y=12_500_000,
                max_zoom=level,
                min_zoom=level,
            )
        )

        z_factor = max(20 * 2 ** (-0.5 * level), 1.7)

        layer.generate_hillshade_tiles(
            tiles,
            options=gdal.DEMProcessingOptions(
                zFactor=z_factor, computeEdges=True, igor=True
            ),
            output=TileOutput(r2_client.maps_dev, "tiles/v1/europe/hillshade"),
        )
