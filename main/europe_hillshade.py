import logging

from osgeo import gdal

from commons import R2Client, S3Client, CompositeTileOutput, BucketTileOutput
from datasets import Glo90, Dataset
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()
    s3_client = S3Client()
    output = CompositeTileOutput(
        [
            BucketTileOutput(r2_client.maps_dev, "tiles/v1/europe/hillshade"),
        ]
    )

    dataset = Glo90()

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

        ElevationTools.generate_hillshade_tiles(
            tile_infos=tiles,
            dataset=dataset.resolve("1k.tif"),
            options=gdal.DEMProcessingOptions(
                zFactor=z_factor, computeEdges=True, igor=True
            ),
            output=output,
        )
