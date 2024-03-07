import logging
from datetime import timedelta

from commons import CompositeTileOutput, BucketTileOutput, R2Client
from datasets import Dataset
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2 = R2Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    tiles = list(WebmercatorTileInfo(zoom=0, x=0, y=0).descendants(max_zoom=10))

    for style in ["light"]:
        dataset = Dataset("Glo90/1k.tif")
        storage_path = f"v1/map/relief-color/{style}"
        ElevationTools.generate_color_relief_tiles(
            tile_infos=tiles,
            dataset=dataset,
            color_filename=f"../../elevation/relief-colors/ubmeteo/{style}",
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=r2.maps_dev,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=r2.maps_prod,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
