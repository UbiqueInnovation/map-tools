import logging

from osgeo import gdal

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from elevation import Glo90, ElevationSwitzerland
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

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
                BucketTileOutput(s3.meteo_swiss_test, storage_path_switzerland),
                BucketTileOutput(s3.meteo_swiss_prod, storage_path_switzerland),
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
                    BucketTileOutput(s3.meteo_swiss_test, storage_path_europe),
                    BucketTileOutput(s3.meteo_swiss_prod, storage_path_europe),
                ]
            ),
        )
