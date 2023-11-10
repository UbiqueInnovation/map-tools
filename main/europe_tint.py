import logging

from commons import R2Client, S3Client, CompositeTileOutput, BucketTileOutput
from elevation import Glo90
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()
    s3_client = S3Client()
    output = CompositeTileOutput(
        [
            BucketTileOutput(r2_client.maps_dev, "tiles/v1/europe/hypsometric"),
            BucketTileOutput(s3_client.dwd_test, "v1/map/europe/tint"),
            BucketTileOutput(s3_client.dwd_prod, "v1/map/europe/tint"),
        ]
    )

    layer = Glo90()

    tiles = list(
        WebmercatorTileInfo.within_bounds(
            min_x=-2_500_000,
            min_y=2_500_000,
            max_x=5_000_000,
            max_y=12_500_000,
            max_zoom=10,
        )
    )

    layer.generate_color_relief_tiles(
        tiles,
        "../elevation/relief-colors/hypsometric-tint",
        output=output,
        input_file_path=f"{layer.data_path}/germany.tif",
    )
