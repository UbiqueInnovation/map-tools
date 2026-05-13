import logging
from datetime import timedelta

from commons import CompositeTileOutput, S3Client, TilePathOutput, BucketStorage
from datasets import Dataset
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3_client = S3Client()

    cache_control_dev = f"max-age={int(timedelta(days=1).total_seconds())}"
    cache_control_int = f"max-age={int(timedelta(days=7).total_seconds())}"
    cache_control_prod = f"max-age={int(timedelta(days=7).total_seconds())}"

    style = "light"
    tiles = list(WebmercatorTileInfo(zoom=4, x=8, y=5).overlapping(max_zoom=10))
    storage_path = "map/hillshade/light"
    dataset = Dataset(f"Viadi/europe-{style}.tif")
    ElevationTools.generate_tiles_for_image(
        dataset=dataset,
        tile_infos=tiles,
        target=dataset.tile_set(f"europe-{style}", "png"),
        src_nodata=150,
        output=CompositeTileOutput(
            [
                TilePathOutput(
                    base_path=storage_path,
                    storage=BucketStorage(
                        bucket=s3_client.viadi_dev,
                        cache_control=cache_control_dev,
                    ),
                ),
                TilePathOutput(
                    base_path=storage_path,
                    storage=BucketStorage(
                        bucket=s3_client.viadi_int,
                        cache_control=cache_control_int,
                    ),
                ),
                TilePathOutput(
                    base_path=storage_path,
                    storage=BucketStorage(
                        bucket=s3_client.viadi_prod,
                        cache_control=cache_control_prod,
                    ),
                ),
            ]
        ),
    )
