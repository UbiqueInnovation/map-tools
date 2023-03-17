import logging
import os
from abc import ABC, abstractmethod
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Iterable

import requests
from alive_progress import alive_bar
from osgeo import gdal
from osgeo_utils.gdal_merge import gdal_merge


class ElevationLayer(ABC):

    @property
    @abstractmethod
    def local_path(self) -> str:
        pass

    @abstractmethod
    def get_urls(self) -> Iterable[str]:
        pass

    @property
    def data_path(self) -> str:
        return f'data/{self.local_path}'

    @property
    def merged_file_path(self) -> str:
        return f'{self.data_path}/merged.tif'

    @property
    def webmercator_file_path(self) -> str:
        return f'{self.data_path}/webmercator.tif'

    @property
    def source_files_path(self) -> str:
        return f'{self.data_path}/source'

    @property
    def source_files(self) -> list[str]:
        path = self.source_files_path
        return [f'{path}/{file}' for file in os.listdir(path) if file.endswith(".tif")]

    def __str__(self) -> str:
        return self.__class__.__name__

    def fetch_tile(self, tile_url: str) -> bool:
        file_name = tile_url.split("/")[-1]
        path = f'{self.source_files_path}/{file_name}'

        if os.path.exists(path):
            return False  # No need to download the fle again

        response = requests.get(tile_url, stream=True)
        if response.status_code != 200:
            raise IOError(f"Could not fetch {tile_url}")

        with open(path, 'wb') as f:
            for chunk in response:
                f.write(chunk)

        logging.debug(f"Saved {tile_url} to {path}")
        return True

    def download_tiles(self) -> None:
        os.makedirs(f'data/{self.local_path}/source', exist_ok=True)

        urls = list(self.get_urls())

        thread_pool = ThreadPool(cpu_count())

        total_count = len(urls)
        downloaded_count = 0

        logging.info(f"Getting tiles from {self}")
        with alive_bar(total_count) as progress_bar:
            for downloaded in thread_pool.imap_unordered(self.fetch_tile, urls):
                progress_bar()
                if downloaded:
                    downloaded_count += 1

        logging.info(f"Downloaded {downloaded_count}, skipped {total_count - downloaded_count} tiles.")

    def merge_tiles(self) -> None:
        if not os.path.exists(self.merged_file_path):
            logging.info(f"Merging tiles for {self}")
            gdal_merge(['', '-o', self.merged_file_path, '-a_nodata', '-999'] + self.source_files)

    def warp_to_webmercator(self) -> None:
        if not os.path.exists(self.webmercator_file_path):
            logging.info(f"Warping tile {self.merged_file_path} to Webmercator")
            gdal.Warp(self.webmercator_file_path, self.merged_file_path, dstSRS='EPSG:3857')
