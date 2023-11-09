import logging

from commons import R2Client, TileOutput
from elevation import Glo90
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2_client = R2Client()

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
        output=TileOutput(r2_client.maps_dev, "tiles/v1/europe/hypsometric"),
    )
