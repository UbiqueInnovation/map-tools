import logging

from azure.storage.blob import ContainerClient, ContentSettings

from tiles import TileInfo
from . import TileOutput


class BlobTileOutput(TileOutput):
    def __init__(
        self,
        container_client: ContainerClient,
        base_path: str,
        cache_control: str = "max-age=86400",  # 1 day
    ) -> None:
        self.container_client = container_client
        self.base_path = base_path
        self.cache_control = cache_control

        logging.getLogger("azure.core").setLevel(logging.WARN)

    def upload(self, file_path: str, tile_info: TileInfo) -> None:
        with open(file_path, "rb") as file:
            self.container_client.upload_blob(
                name=f"{self.base_path}/{tile_info.path}.png",
                data=file,
                overwrite=True,
                content_settings=ContentSettings(
                    cache_control=self.cache_control, content_type="image/png"
                ),
            )
