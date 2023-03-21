import logging
import os
from abc import ABC, abstractmethod
from collections import defaultdict
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Iterable

from PIL import Image
from alive_progress import alive_bar, alive_it
from osgeo import gdal
from requests import Session
from requests.adapters import HTTPAdapter
from retry import retry

from storage import TileOutput
from tiles import TileInfo


class ElevationLayer(ABC):

    def __init__(self, output: TileOutput = None) -> None:
        self.num_threads = cpu_count()
        self.output = output
        self.thread_pool = ThreadPool(self.num_threads)
        self.session = Session()
        self.session.mount('https://', HTTPAdapter(pool_connections=self.num_threads, pool_maxsize=self.num_threads))

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
    def virtual_dataset_file_path(self) -> str:
        return f'{self.data_path}/source.vrt'

    @property
    def source_files_path(self) -> str:
        return f'{self.data_path}/source'

    @property
    def warped_tiles_path(self) -> str:
        return f'{self.data_path}/warped'

    @property
    def hillshade_tiles_path(self) -> str:
        return f'{self.data_path}/hillshade'

    @property
    def source_files(self) -> list[str]:
        path = self.source_files_path
        return [f'{path}/{file}' for file in os.listdir(path) if file.endswith(".tif")]

    def warped_tile_path(self, tile_info: TileInfo) -> str:
        return f'{self.warped_tiles_path}/{tile_info.path}.tif'

    def hillshade_tile_path(self, tile_info: TileInfo) -> str:
        return f'{self.hillshade_tiles_path}/{tile_info.path}.png'

    def __str__(self) -> str:
        return self.__class__.__name__

    @retry(tries=5, delay=.1, backoff=2)
    def fetch_tile(self, tile_url: str) -> bool:
        file_name = tile_url.split("/")[-1]
        path = f'{self.source_files_path}/{file_name}'

        if os.path.exists(path):
            return False  # No need to download the fle again

        response = self.session.get(tile_url, stream=True)
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

        total_count = len(urls)
        downloaded_count = 0

        logging.info(f"Getting tiles from {self}")
        with alive_bar(total_count) as progress_bar:
            for downloaded in self.thread_pool.imap_unordered(self.fetch_tile, urls):
                progress_bar()
                if downloaded:
                    downloaded_count += 1

        logging.info(f"Downloaded {downloaded_count}, skipped {total_count - downloaded_count} tiles.")

    def create_virtual_dataset(self) -> None:
        if os.path.exists(self.virtual_dataset_file_path):
            logging.info("Virtual data set already exists")
            return

        logging.info("Creating virtual data set")
        gdal.BuildVRT(
            destName=self.virtual_dataset_file_path,
            srcDSOrSrcDSTab=self.source_files,
            resolution='highest',
            VRTNodata=-999)

    def cut_and_warp_to_tile(self, tile_info: TileInfo, resolution: int = 512) -> None:
        target_path = self.warped_tile_path(tile_info)
        if os.path.exists(target_path):
            return

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        min_x, min_y = tile_info.min_coordinate
        max_x, max_y = tile_info.max_coordinate
        gdal.Warp(
            destNameOrDestDS=target_path,
            srcDSOrSrcDSTab=self.virtual_dataset_file_path,
            dstSRS='EPSG:3857',
            width=resolution,
            height=resolution,
            outputBounds=(min_x, min_y, max_x, max_y)
        )

    def generate_hillshade_tile(self, tile_info: TileInfo):
        target_path = self.hillshade_tile_path(tile_info)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        gdal.DEMProcessing(
            destName=target_path,
            srcDS=self.warped_tile_path(tile_info),
            processing='hillshade',
            multiDirectional=True,
            computeEdges=True
        )

    @staticmethod
    def image_to_rgb(path: str) -> None:
        Image.open(path).convert('RGBA').save(path)

    def generate_tile(self, tile_info: TileInfo) -> None:
        self.cut_and_warp_to_tile(tile_info)
        self.generate_hillshade_tile(tile_info)
        self.image_to_rgb(self.hillshade_tile_path(tile_info))
        if self.output:
            self.output.upload(self.hillshade_tile_path(tile_info), tile_info)

    def generate(self, tile_infos: Iterable[TileInfo]) -> None:
        self.download_tiles()
        self.create_virtual_dataset()

        tile_infos_by_level = defaultdict(list)
        for tile_info in tile_infos:
            tile_infos_by_level[tile_info.zoom].append(tile_info)

        for level, tile_infos_of_level in tile_infos_by_level.items():
            logging.info(f"Generating tiles for level {level}")
            list(alive_it(self.thread_pool.imap_unordered(self.generate_tile, tile_infos_of_level),
                          total=len(tile_infos_of_level)))
