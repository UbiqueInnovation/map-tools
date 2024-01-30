import logging
from datetime import timedelta

from osgeo import gdal

from commons import CompositeTileOutput, BlobTileOutput, AzureClient
from datasets import SwissAlti3d
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    azure_client = AzureClient()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    tiles_switzerland = list(
        WebmercatorTileInfo(zoom=6, x=33, y=22).overlapping(max_zoom=12)
    )
    storage_path = "v1/hillshade/switzerland/light"
    ElevationTools.generate_hillshade_tiles(
        dataset=SwissAlti3d().resolve("5m.cut.tif"),
        tile_infos=tiles_switzerland,
        options=gdal.DEMProcessingOptions(zFactor=1.7, computeEdges=True, igor=True),
        output=CompositeTileOutput(
            [
                BlobTileOutput(
                    container_client=azure_client.flesk_dev,
                    base_path=storage_path,
                    cache_control=cache_control_test,
                ),
                BlobTileOutput(
                    container_client=azure_client.flesk_prod,
                    base_path=storage_path,
                    cache_control=cache_control_prod,
                ),
            ]
        ),
    )
