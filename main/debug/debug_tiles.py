import os
from datetime import timedelta
from random import randint

from PIL import Image, ImageDraw, ImageFont

from commons import R2Client, BucketTileOutput, CompositeTileOutput
from elevation import ElevationTools
from tiles import TileInfo, WebmercatorTileInfo


def create_png(tile: TileInfo) -> Image:
    r, g, b = (randint(0, 128), randint(0, 128), randint(0, 128))
    image = Image.new("RGBA", (256, 256), (r, g, b, 50))
    draw = ImageDraw.Draw(image)

    draw.rectangle([(0, 0), (255, 255)], outline=(r, g, b, 255), width=5)

    font = ImageFont.truetype("Arial.ttf", size=36)
    text = f"z: {tile.zoom}\nx: {tile.x}\ny: {tile.y}"
    draw.text((10, 10), text, fill=(r, g, b, 255), font=font)

    return image


def main() -> None:
    r2 = R2Client()

    max_age = int(timedelta(days=1).total_seconds())
    cache_control = f"max-age={max_age}"
    output = CompositeTileOutput(
        [
            BucketTileOutput(
                bucket=r2.maps_dev,
                base_path=f"v1/map/4326/debug",
                cache_control=cache_control,
            ),
            BucketTileOutput(
                bucket=r2.maps_dev,
                base_path=f"v1/map/3857/debug",
                cache_control=cache_control,
            ),
        ]
    )

    def create_debug_tile(tile: TileInfo) -> None:
        path = f"{tile.path}.png"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        create_png(tile).save(path)
        output.upload(path, tile)

    tiles = WebmercatorTileInfo.all_tiles(max_zoom=8)
    ElevationTools.apply_for_all_tile_infos(tiles, create_debug_tile)


# Example usage
if __name__ == "__main__":
    main()
