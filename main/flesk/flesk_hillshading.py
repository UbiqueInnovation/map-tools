import logging
from datetime import timedelta

from commons import CompositeTileOutput, BlobTileOutput, AzureClient
from datasets import Dataset
from elevation import ElevationTools
from tiles import WebmercatorTileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    azure_client = AzureClient()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=7).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    style = "light"
    tiles = list(WebmercatorTileInfo(zoom=4, x=8, y=5).overlapping(max_zoom=10))
    storage_path = f"v1/hillshade/europe/{style}"
    dataset = Dataset(f"MeteoSwiss/europe-{style}.tif")
    ElevationTools.generate_tiles_for_image(
        dataset=dataset,
        tile_infos=tiles,
        target=dataset.tile_set(f"europe-{style}", "png"),
        src_nodata=150,
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
