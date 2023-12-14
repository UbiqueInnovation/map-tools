import logging
import os
from abc import abstractmethod, ABC
from typing import Iterable

from osgeo import gdal

from commons import FileDownloader
from . import Dataset


class DownloadableDataset(Dataset, ABC):
    def __init__(self, name: str) -> None:
        super().__init__(f"{name}/data.vrt")
        self.data_path = f"{self.base_path}/data"

    @abstractmethod
    def get_urls(self) -> Iterable[str]:
        pass

    def download(self) -> None:
        path = self.data_path

        os.makedirs(path, exist_ok=True)
        FileDownloader.download_all(self.get_urls(), path)

        if os.path.exists(self.path):
            return

        logging.info("Creating virtual data set")
        files = [f"{path}/{file}" for file in os.listdir(path) if file.endswith(".tif")]
        gdal.BuildVRT(
            destName=self.path,
            srcDSOrSrcDSTab=files,
            options=gdal.BuildVRTOptions(resolution="highest", VRTNodata=0),
        )
