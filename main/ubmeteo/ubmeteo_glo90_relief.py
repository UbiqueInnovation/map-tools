import logging
from datetime import timedelta

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from datasets import Dataset
from elevation import ElevationTools
from tiles import Wgs84TileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    style = "light"
    max_zoom = 9
    source_width, source_height = 432_000, 210_000
    tile_width = round(source_width / 2 ** max_zoom)
    tile_height = round(source_height / 2 ** max_zoom)

    logging.info(f"Creating tiles of size {tile_width}x{tile_height}")
    dataset_to_tiles = {
        f"Fluid/glo90-{style}-medium.tif": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(max_zoom=4)
        ),
        f"Fluid/glo90-{style}.tif": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=5, max_zoom=max_zoom)
        ),
    }

    for dataset_path, tiles in dataset_to_tiles.items():
        storage_path = f"v1/map/4326/hillshade/{style}"
        dataset = Dataset(dataset_path)
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles,
            dataset=dataset,
            src_nodata=150,
            target=dataset.tile_set(f"{style}-4326", "png"),
            resample_alg="lanczos",
            width=tile_width,
            height=tile_height,
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=s3.fluid_app_dev,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=s3.fluid_app_prod,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
