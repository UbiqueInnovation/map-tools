import logging
from datetime import timedelta

from commons import S3Client, CompositeTileOutput, BucketTileOutput
from datasets import Dataset
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    base_tile = WebmercatorTileInfo(zoom=4, x=8, y=5)

    tiles_europe = list(
        WebmercatorTileInfo.within_bounds(
            min_x=-1_669_792,  # lon -15
            min_y=4_163_873,  # lat 35
            max_x=3_896_223,  # lon 35
            max_y=9_100_251,  # lat 63
            max_zoom=10,
        )
    )

    for style in ["light", "dark"]:
        storage_path = f"map/v1/europe/hillshade/{style}"
        dataset = Dataset(f"DWD/europe-{style}.tif")
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles_europe,
            dataset=dataset,
            target=dataset.tile_set(f"europe-{style}", "png"),
            src_nodata=150,
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=s3.dwd_test,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=s3.dwd_prod,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
