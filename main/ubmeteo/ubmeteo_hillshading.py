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

    tiles = list(WebmercatorTileInfo(zoom=0, x=0, y=0).descendants(max_zoom=8))

    for style in ["light"]:
        storage_path = f"v1/map/hillshade/{style}"
        dataset = Dataset(f"Glo90/hillshade-{style}.tif")
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles,
            dataset=dataset,
            target=dataset.tile_set(f"hillshade-{style}", "png"),
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
