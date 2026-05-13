import logging
from datetime import timedelta

from commons import CompositeTileOutput, TilePathOutput, S3Client
from commons.bucket_storage import BucketStorage
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

    tiles_europe = list(WebmercatorTileInfo(zoom=4, x=8, y=5).overlapping(max_zoom=10))
    for style in ["light", "dark"]:
        storage_path_europe = f"map/hillshade/europe/{style}"
        dataset = Dataset(f"MeteoSwiss/europe-{style}.tif")
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles_europe,
            dataset=dataset,
            target=dataset.tile_set(f"europe-{style}", "png"),
            src_nodata=150,
            output=CompositeTileOutput(
                [
                    TilePathOutput(
                        base_path=storage_path_europe,
                        storage=BucketStorage(
                            bucket=s3.meteo_swiss_test,
                            cache_control=cache_control_test,
                        ),
                    ),
                    TilePathOutput(
                        base_path=storage_path_europe,
                        storage=BucketStorage(
                            bucket=s3.meteo_swiss_prod,
                            cache_control=cache_control_prod,
                        ),
                    ),
                ]
            ),
        )
