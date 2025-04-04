import logging
import os
from datetime import timedelta
from pathlib import Path

import numpy as np
import rasterio
from alive_progress import alive_it
from osgeo import gdal

from commons import CompositeTileOutput, BucketTileOutput, S3Client
from datasets import Glo90
from elevation import ElevationTools
from tiles import Wgs84TileInfo


def create_tile(
    tile: Wgs84TileInfo, width: int = 0, height: int = 0
):
    dataset = Glo90().resolve("glo90.tif")
    warped_path = dataset.resolve("warped/4326/" + tile.path + ".tif").path
    if not os.path.exists(warped_path):
        os.makedirs(os.path.dirname(warped_path), exist_ok=True)
        gdal.Warp(
            destNameOrDestDS=warped_path,
            srcDSOrSrcDSTab=dataset.path,
            options=gdal.WarpOptions(
                outputBounds=tile.bounds_min_x_min_y_max_x_max_y,
                dstNodata=0,
                width=width,
                height=height,
                resampleAlg="bilinear",
            ),
        )

    png_path = dataset.resolve("elevation/4326/" + tile.path + ".png").path
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(png_path):
        with rasterio.open(warped_path) as src:
            dem = src.read(1)

        dem = np.round(dem, -1)

        r = np.zeros(dem.shape)
        g = np.zeros(dem.shape)
        b = np.zeros(dem.shape)

        r += np.floor_divide((100000 + dem * 10), 256**2)
        g += np.floor_divide((100000 + dem * 10), 256) - r * 256
        b += np.floor(100000 + dem * 10) - r * 65536 - g * 256

        meta = src.meta
        meta["dtype"] = rasterio.uint8
        meta["nodata"] = 0
        meta["count"] = 3
        meta["driver"] = "png"

        with rasterio.open(png_path, "w", **meta) as dst:
            dst.write_band(1, r.astype(rasterio.uint8))
            dst.write_band(2, g.astype(rasterio.uint8))
            dst.write_band(3, b.astype(rasterio.uint8))

        output.upload(png_path, tile)

    os.remove(png_path)
    os.remove(warped_path)


def create_downscaled_tile(tile: Wgs84TileInfo):
    create_tile(tile, width=512, height=256)


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    s3 = S3Client()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"
    storage_path = "v1/map/4326/elevation"
    output = CompositeTileOutput(
        [
            BucketTileOutput(
                bucket=s3.fluid_app_dev,
                base_path=storage_path,
                cache_control=cache_control_test,
            ),
            BucketTileOutput(
                bucket=s3.fluid_app_prod,
                base_path=storage_path,
                cache_control=cache_control_prod,
            ),
        ]
    )

    gdal.UseExceptions()
    base_tile = Wgs84TileInfo(zoom=0, x=0, y=0)

    for target_zoom in range(0, 11):
        tiles = list(base_tile.descendants(target_zoom, target_zoom))
        print(f"Generating at level {target_zoom} within bounds {base_tile.bounds}")

        apply_function = ElevationTools.thread_pool.imap_unordered(
            create_tile if target_zoom == 10 else create_downscaled_tile, tiles
        )
        list(alive_it(apply_function, total=len(tiles)))
