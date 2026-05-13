from datetime import timedelta
from io import BytesIO
from random import randint

from PIL import Image, ImageDraw, ImageFont

from commons import R2Client, PMTilesOutput
from commons.bucket_storage import BucketStorage
from elevation import ElevationTools
from tiles import TileInfo, WebmercatorTileInfo


def create_image(tile: TileInfo) -> Image:
    r, g, b = (randint(0, 128), randint(0, 128), randint(0, 128))
    image = Image.new("RGBA", (256, 256), (r, g, b, 50))
    draw = ImageDraw.Draw(image)

    draw.rectangle([(0, 0), (255, 255)], outline=(r, g, b, 255), width=5)

    font = ImageFont.truetype("Arial.ttf", size=36)
    text = f"z: {tile.zoom}\nx: {tile.x}\ny: {tile.y}"
    draw.text((10, 10), text, fill=(r, g, b, 255), font=font)

    return image


def main() -> None:

    pmtiles_path = "debug.pmtiles"
    with open(pmtiles_path, "wb") as f:
        pmtiles_output = PMTilesOutput(f)

        def create_debug_tile(tile: TileInfo) -> None:
            with BytesIO() as buffer:
                create_image(tile).save(buffer, "webp")
                pmtiles_output.save_bytes(buffer.getvalue(), tile)

        tiles = WebmercatorTileInfo.all_tiles(max_zoom=8)
        ElevationTools.apply_for_all_tile_infos(tiles, create_debug_tile)

        pmtiles_output.finalize()

    r2 = R2Client()

    max_age = int(timedelta(days=1).total_seconds())
    cache_control = f"max-age={max_age}"
    storage = BucketStorage(r2.maps_dev, cache_control=cache_control)
    storage.save(pmtiles_path, target_path="v1/map/4326/debug.pmtiles")
    storage.save(pmtiles_path, target_path="v1/map/3857/debug.pmtiles")


# Example usage
if __name__ == "__main__":
    main()
