import logging

from osgeo import gdal

from commons import R2Client, S3Client, CompositeTileOutput, BucketTileOutput
from elevation import Glo90
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()
    s3_client = S3Client()
    output = CompositeTileOutput(
        [
            BucketTileOutput(s3_client.dwd_test, "v1/map/germany/hillshade"),
            BucketTileOutput(s3_client.dwd_prod, "v1/map/germany/hillshade"),
        ]
    )

    layer = Glo90()

    for level in range(0, 11):
        tiles = list(
            WebmercatorTileInfo(zoom=4, x=8, y=5).overlapping(
                max_zoom=level,
                min_zoom=level,
            )
        )

        z_factor = max(20 * 2 ** (-0.5 * level), 3)

        layer.generate_hillshade_tiles(
            tiles,
            options=gdal.DEMProcessingOptions(
                zFactor=z_factor, computeEdges=True, igor=True
            ),
            output=output,
            input_file_path=f"{layer.data_path}/germany.tif",
        )
