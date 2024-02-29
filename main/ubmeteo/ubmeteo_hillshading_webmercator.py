import logging
from datetime import timedelta

from commons import CompositeTileOutput, R2Client, BucketTileOutput
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

    style = "light"
    dataset_to_tiles = {
        # f"Glo90/hillshading/{style}-small.tif": list(
        #     WebmercatorTileInfo(zoom=0, x=0, y=0).descendants(max_zoom=5)
        # ),
        f"Glo90/hillshading/{style}.vrt": list(
            WebmercatorTileInfo(zoom=1, x=1, y=0).descendants(min_zoom=10, max_zoom=10)
        ),
    }

    for dataset_path, tiles in dataset_to_tiles.items():
        storage_path = f"v1/map/3857/hillshade/{style}"
        dataset = Dataset(dataset_path)
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles,
            dataset=dataset,
            src_nodata=150,
            target=dataset.tile_set(f"hillshade-{style}", "png"),
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=r2.ubmeteo_app_dev,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=r2.ubmeteo_app_prod,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
