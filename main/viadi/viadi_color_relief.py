import logging
from datetime import timedelta

from commons import CompositeTileOutput, TilePathOutput, S3Client, BucketStorage
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
        color_filename="../../elevation/relief-colors/light",
        tile_infos=tiles,
        output=CompositeTileOutput(
            [
                TilePathOutput(
                    base_path=storage_path_color_relief,
                    storage=BucketStorage(
                        bucket=s3.viadi_dev,
                        cache_control=cache_control_dev,
                    ),
                ),
                TilePathOutput(
                    base_path=storage_path_color_relief,
                    storage=BucketStorage(
                        bucket=s3.viadi_prod,
                        cache_control=cache_control_prod,
                    ),
                ),
            ]
        ),
    )
