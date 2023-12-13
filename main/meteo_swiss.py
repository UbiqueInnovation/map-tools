import logging
from datetime import timedelta

from osgeo import gdal

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from elevation import Glo90, ElevationSwitzerland
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    tiles_switzerland = list(
        WebmercatorTileInfo(zoom=6, x=33, y=22).overlapping(max_zoom=12)
    )
    layer_switzerland = ElevationSwitzerland()
    storage_path_switzerland = "v1/map/hillshade/switzerland/light"
    layer_switzerland.generate_hillshade_tiles(
        tiles_switzerland,
        input_file_path=f"{layer_switzerland.data_path}/5m.cut.tif",
        options=gdal.DEMProcessingOptions(zFactor=1.7, computeEdges=True, igor=True),
        output=CompositeTileOutput(
            [
                BucketTileOutput(
                    bucket=s3.meteo_swiss_test,
                    base_path=storage_path_switzerland,
                    cache_control=cache_control_test,
                ),
                BucketTileOutput(
                    bucket=s3.meteo_swiss_prod,
                    base_path=storage_path_switzerland,
                    cache_control=cache_control_prod,
                ),
            ]
        ),
    )

    layer_europe = Glo90()
    tiles_europe = list(WebmercatorTileInfo(zoom=4, x=8, y=5).overlapping(max_zoom=10))
    for style in ["light", "dark"]:
        storage_path_europe = f"v1/map/hillshade/europe/{style}"
        layer_europe.generate_tiles_for_image(
            tiles_europe,
            input_file_path=f"{layer_europe.data_path}/meteo-swiss-europe-{style}.tif",
            output_folder=f"{layer_europe.data_path}/meteo-swiss-europe-{style}",
            src_nodata=150,
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=s3.meteo_swiss_test,
                        base_path=storage_path_europe,
                        cache_control=cache_control_test,
                    ),
                    BucketTileOutput(
                        bucket=s3.meteo_swiss_prod,
                        base_path=storage_path_europe,
                        cache_control=cache_control_prod,
                    ),
                ]
            ),
        )
