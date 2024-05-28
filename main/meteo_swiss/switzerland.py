import logging
from datetime import timedelta

from osgeo import gdal

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from datasets import SwissAlti3d
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    base_tile = WebmercatorTileInfo(zoom=6, x=33, y=22)
    tiles_for_file = {
        "10m.cut.tif": base_tile.overlapping(max_zoom=8),
        "5m.cut.tif": base_tile.overlapping(min_zoom=9, max_zoom=12),
    }
    storage_path = "map/hillshade/switzerland/light"
    for file, tiles in tiles_for_file.items():
        ElevationTools.generate_hillshade_tiles(
            dataset=SwissAlti3d().resolve(file),
            tile_infos=tiles,
            options=gdal.DEMProcessingOptions(
                zFactor=1.7, computeEdges=True, igor=True
            ),
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=s3.meteo_swiss_test,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=s3.meteo_swiss_prod,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
