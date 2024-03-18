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
    tiles_and_cutline = [
        (base_tile.overlapping(max_zoom=8), "cutline-germany-5M.gpkg"),
        (base_tile.overlapping(min_zoom=9, max_zoom=10), "cutline-germany-250k.gpkg"),
    ]
    for tiles, cutline in tiles_and_cutline:
        for style in ["light", "dark"]:
            storage_path_hillshade = f"map/v1/germany/hillshade/{style}"
            dataset = Dataset(f"DWD/germany-{style}.tif")
            ElevationTools.generate_tiles_for_image(
                tile_infos=tiles,
                dataset=dataset,
                target=dataset.tile_set(f"germany-{style}", "png"),
                src_nodata=0,
                cutline=dataset.resolve(cutline).path,
                output=CompositeTileOutput(
                    [
                        BucketTileOutput(
                            bucket=s3.dwd_test,
                            base_path=storage_path_hillshade,
                            cache_control=cache_control_test,
                        ),
                        BucketTileOutput(
                            bucket=s3.dwd_prod,
                            base_path=storage_path_hillshade,
                            cache_control=cache_control_prod,
                        ),
                    ]
                ),
            )
