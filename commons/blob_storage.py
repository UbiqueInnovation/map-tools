import logging
import os
from typing import override, Optional

from azure.storage.blob import ContainerClient, ContentSettings

from . import Storage


class BlobStorage(Storage):

    def __init__(
        self,
        container_client: ContainerClient,
        cache_control: str = "max-age=86400",  # 1 day
    ) -> None:
        self.container_client = container_client
        self.cache_control = cache_control

        logging.getLogger("azure.core").setLevel(logging.WARN)

    @override
    def save(
        self,
        file_path: str,
        target_path: str,
        content_type: Optional[str] = None,
    ) -> None:
        if os.stat(file_path).st_size == 0:
            logging.warning(f"File {file_path} is empty")

        with open(file_path, "rb") as file:
            self.container_client.upload_blob(
                name=target_path,
                data=file,
                overwrite=True,
                content_settings=ContentSettings(
                    cache_control=self.cache_control,
                    content_type=content_type,
                ),
            )
