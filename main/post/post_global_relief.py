import json
import logging
from datetime import timedelta
from io import BytesIO

from commons import CompositeTileOutput, BucketTileOutput, R2Client, BucketOutput
from datasets import Dataset
from elevation import ElevationTools
from tiles import Wgs84TileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    r2 = R2Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    style = "light"
    max_zoom = 9
    source_width, source_height = 432_000, 210_000
    tile_width = round(source_width / 2**max_zoom)
    tile_height = round(source_height / 2**max_zoom)

    dataset_to_tiles = {
        f"Glo90/hillshading/{style}-small.tif": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(max_zoom=5)
        ),
        f"Glo90/hillshading/{style}-medium.tif": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=6, max_zoom=8)
        ),
        f"Glo90/hillshading/{style}.vrt": list(
            Wgs84TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=9, max_zoom=max_zoom)
        ),
    }

    for bucket in [r2.post_playground, r2.post_playground_int]:
        with BytesIO() as file:
            tile_json = dict(
                tilejson="3.0.0",
                name="global-relief",
                version="1.0.0",
                format="jpeg",
                tiles=[
                    "https://post-playground-dev.openmobilemaps.io/v1/background/global-relief/light/4326/{z}/{x}/{y}.jpg"
                ],
                minzoom=0,
                maxzoom=max_zoom,
            )
            file.write(json.dumps(tile_json).encode("UTF-8"))
            file.flush()
            file.seek(0)
            BucketOutput(
                bucket=bucket,
                cache_control=cache_control_test,
            ).upload(file, f"v1/background/global-relief/{style}/tiles.json")

    for dataset_path, tiles in dataset_to_tiles.items():
        storage_path = f"v1/background/global-relief/{style}/4326"
        dataset = Dataset(dataset_path)
        ElevationTools.generate_tiles_for_image(
            tile_infos=tiles,
            dataset=dataset,
            width=tile_width,
            height=tile_height,
            src_nodata=150,
            target=dataset.tile_set(f"{style}-4326", "jpg"),
            creation_options=dict(QUALITY=90),
            resample_alg="bilinear",
            output=CompositeTileOutput(
                [
                    BucketTileOutput(
                        bucket=r2.post_playground,
                        base_path=storage_path,
                        cache_control=cache_control_test,
                        file_ending="jpg",
                    ),
                    BucketTileOutput(
                        bucket=r2.post_playground_int,
                        base_path=storage_path,
                        cache_control=cache_control_prod,
                        file_ending="jpg",
                    )
                ]
            ),
        )
