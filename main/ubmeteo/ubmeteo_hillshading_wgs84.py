import logging
from datetime import timedelta

from commons import CompositeTileOutput, R2Client, BucketTileOutput, S3Client
from datasets import Dataset
from elevation import ElevationTools
from tiles import Wgs84TileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2 = R2Client()
    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    style = "light"
    dataset_to_tiles = {
        # f"Glo90/hillshading/{style}-small.tif": list(
        #     Wgs84TileInfo(zoom=0, x=0, y=0).descendants(max_zoom=5)
        # ),
        f"Glo90/hillshading/{style}.vrt": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=0, max_zoom=10)
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
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=s3.fluid_app_dev,
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
