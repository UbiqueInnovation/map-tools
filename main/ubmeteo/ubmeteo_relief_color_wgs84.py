import logging
from datetime import timedelta

from commons import CompositeTileOutput, TilePathOutput, S3Client, BucketStorage
from datasets import Glo90
from elevation import ElevationTools
from tiles import Wgs84TileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    for level in range(0, 8 + 1):
        style = "light"
        storage_path = f"v1/map/4326/relief-color/{style}"
        dataset = (
            Glo90().resolve("Glo90.tif")
            if level >= 6
            else Glo90().resolve("global_1km.tif")
        )
        tiles = list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=level, max_zoom=level)
        )
        ElevationTools.generate_color_relief_tiles(
            tile_infos=tiles,
            dataset=dataset,
            color_filename=f"../../elevation/relief-colors/ubmeteo/{style}",
            output=CompositeTileOutput(
                [
                    TilePathOutput(
                        base_path=storage_path,
                        storage=BucketStorage(
                            bucket=s3.fluid_app_dev,
                            cache_control=cache_control_test,
                        ),
                    ),
                    TilePathOutput(
                        base_path=storage_path,
                        storage=BucketStorage(
                            bucket=s3.fluid_app_prod,
                            cache_control=cache_control_prod,
                        ),
                    ),
                ]
            ),
        )
