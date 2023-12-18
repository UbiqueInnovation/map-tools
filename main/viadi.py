import logging
from datetime import timedelta

from osgeo import gdal

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from datasets import SwissAlti3d
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_dev = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_dev = f"max-age={max_age_dev}"
    cache_control_prod = f"max-age={max_age_prod}"

    tiles = list(WebmercatorTileInfo(zoom=6, x=33, y=22).overlapping(max_zoom=12))

    storage_path_color_relief = "map/color-relief"
    ElevationTools.generate_color_relief_tiles(
        dataset=SwissAlti3d().resolve("5m.cut.tif"),
        color_filename="../elevation/relief-colors/light",
        tile_infos=tiles,
        output=CompositeTileOutput(
            [
                BucketTileOutput(
                    bucket=s3.viadi_dev,
                    base_path=storage_path_color_relief,
                    cache_control=cache_control_dev,
                ),
                BucketTileOutput(
                    bucket=s3.viadi_prod,
                    base_path=storage_path_color_relief,
                    cache_control=cache_control_prod,
                ),
            ]
        ),
    )

    storage_path_hillshade = "map/hillshade/light"
    ElevationTools.generate_hillshade_tiles(
        dataset=SwissAlti3d().resolve("5m.cut.tif"),
        tile_infos=tiles,
        options=gdal.DEMProcessingOptions(zFactor=1.7, computeEdges=True, igor=True),
        output=CompositeTileOutput(
            [
                BucketTileOutput(
                    bucket=s3.viadi_dev,
                    base_path=storage_path_hillshade,
                    cache_control=cache_control_dev,
                ),
                BucketTileOutput(
                    bucket=s3.viadi_prod,
                    base_path=storage_path_hillshade,
                    cache_control=cache_control_prod,
                ),
            ]
        ),
    )
