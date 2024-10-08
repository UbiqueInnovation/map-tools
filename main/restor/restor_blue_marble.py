import logging
from datetime import timedelta
from multiprocessing.pool import ThreadPool

from commons import CompositeTileOutput, BlobTileOutput, AzureClient
from datasets.blue_marble import BlueMarble
from elevation import ElevationTools
from tiles import Wgs84TileInfo

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    azure_client = AzureClient()

    max_age_test = int(timedelta(days=1).total_seconds())
    max_age_prod = int(timedelta(days=180).total_seconds())
    cache_control_test = f"max-age={max_age_test}"
    cache_control_prod = f"max-age={max_age_prod}"

    dataset = BlueMarble()
    max_zoom = 7
    tiles = list(Wgs84TileInfo.all_tiles(max_zoom=max_zoom))
    storage_path = f"v1/map/4362/blue_marble/{dataset.layer}/{dataset.date}"

    tile_width = round(dataset.source_width / 2**max_zoom)
    tile_height = round(dataset.source_height / 2**max_zoom)

    ElevationTools.thread_pool = ThreadPool(10)
    ElevationTools.generate_tiles_for_image(
        tile_infos=tiles,
        dataset=dataset,
        width=tile_width,
        height=tile_height,
        target=dataset.tile_set("tiles/4326", "jpg"),
        creation_options=dict(QUALITY=90),
        resample_alg="bilinear",
        output=CompositeTileOutput(
            [
                BlobTileOutput(
                    container_client=azure_client.restor_dev,
                    base_path=storage_path,
                    cache_control=cache_control_test,
                    file_extension="jpg",
                ),
                BlobTileOutput(
                    container_client=azure_client.restor_prod,
                    base_path=storage_path,
                    cache_control=cache_control_prod,
                    file_extension="jpg",
                ),
            ]
        ),
    )
