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
    zoom = 10

    tiles = list(
        Wgs84TileInfo(zoom=0, x=0, y=0).within_bounds(
            min_zoom=zoom,
            max_zoom=zoom,
            min_lat=34.3,
            min_lon=-11,
            max_lat=71.5,
            max_lon=32,
        )
    )

    dataset = Dataset(f"Fluid/post-30-{style}.tif")

    storage_path = f"v1/map/4326/hillshade/{style}"
    ElevationTools.generate_tiles_for_image(
        tile_infos=tiles,
        dataset=dataset,
        src_nodata=150,
        target=dataset.tile_set(f"{style}-4326", "png"),
        resample_alg="bilinear",
        # Use native width and height
        width=0,
        height=0,
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
