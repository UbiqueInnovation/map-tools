import logging
import os
from abc import ABC, abstractmethod
from collections import defaultdict
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Iterable, Callable, Sequence

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from alive_progress import alive_it
from osgeo import gdal, gdalconst
from requests import Session
from requests.adapters import HTTPAdapter
from retry import retry

from commons import TileOutput, FileDownloader
from tiles import TileInfo


class ElevationLayer(ABC):

    def __init__(self, output: TileOutput = None) -> None:
        self.num_threads = cpu_count()
        self.output = output
        self.thread_pool = ThreadPool(self.num_threads)
        self.session = Session()
        self.session.mount('https://', HTTPAdapter(pool_connections=self.num_threads, pool_maxsize=self.num_threads))

        # Set environment variables for GDAL
        os.environ['GDAL_PAM_ENABLED'] = 'NO'
        os.environ['GDAL_MAX_DATASET_POOL_SIZE'] = f'{self.num_threads}'

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

    def hillshade_base_path(self, tile_info: TileInfo) -> str:
        return f'{self.hillshade_tiles_path}/{tile_info.path}'

    def hillshade_tile_path(self, tile_info: TileInfo, key: str = None) -> str:
        return f'{self.hillshade_base_path(tile_info)}{f"_{key}" if key else ""}.png'

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
        FileDownloader.download_all(self.get_urls(), self.source_files_path)

    def create_virtual_dataset(self) -> None:
        if os.path.exists(self.virtual_dataset_file_path):
            logging.info("Virtual data set already exists")
            return

        logging.info("Creating virtual data set")
        gdal.BuildVRT(
            destName=self.virtual_dataset_file_path,
            srcDSOrSrcDSTab=self.source_files,
            options=gdal.BuildVRTOptions(resolution='highest', VRTNodata=0))

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
            options=gdal.WarpOptions(
                dstSRS=tile_info.srs,
                width=resolution,
                height=resolution,
                resampleAlg=gdalconst.GRA_CubicSpline,
                outputBounds=(min_x, min_y, max_x, max_y),
                multithread=True,
            )
        )

    def process_hillshade(self, tile_info: TileInfo, options: gdal.DEMProcessingOptions = None, key: str = None):
        target_path = self.hillshade_tile_path(tile_info, key)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        gdal.DEMProcessing(
            destName=target_path,
            srcDS=self.warped_tile_path(tile_info),
            processing='hillshade',
            options=options or gdal.DEMProcessingOptions(computeEdges=True, igor=True)
        )

    @staticmethod
    def image_to_rgb(path: str) -> None:
        Image.open(path).convert('RGBA').save(path)

    @staticmethod
    def multiply_images(paths: Sequence[str]) -> Image:
        if len(paths) == 1:
            return Image.open(paths[0])
        else:
            return ImageChops.multiply(Image.open(paths[0]), ElevationLayer.multiply_images(paths[1:]))

    @staticmethod
    def adjust_image(source: str, target: str, brightness: float = 1, contrast: float = 1, gamma: float = 1) -> None:
        source_image = Image.open(source).convert('RGBA')
        brightness_adjusted = ImageEnhance.Brightness(source_image).enhance(brightness)
        gamma_adjusted = ElevationLayer.adjust_gamma(brightness_adjusted, gamma)
        contrast_adjusted = ImageEnhance.Contrast(gamma_adjusted).enhance(contrast)
        contrast_adjusted.save(target)

    @staticmethod
    def adjust_gamma(image: Image, gamma: float) -> Image:
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")
        return Image.fromarray(cv2.LUT(np.asarray(image), table))

    def generate_hillshade_tile(self, tile_info: TileInfo, passes: dict[str, dict] = None) -> None:
        self.cut_and_warp_to_tile(tile_info)
        target_path = self.hillshade_tile_path(tile_info)
        if passes:
            for key, arguments in passes.items():
                self.process_hillshade(tile_info, arguments['options'], key)
                self.adjust_image(f"{self.hillshade_base_path(tile_info)}_{key}.png",
                                  f"{self.hillshade_base_path(tile_info)}_{key}_adjusted.png",
                                  **arguments.get('corrections', dict()))

            paths = [f"{self.hillshade_base_path(tile_info)}_{key}_adjusted.png" for key in passes.keys()]
            self.multiply_images(paths).save(target_path)

        else:
            self.process_hillshade(tile_info)
            self.image_to_rgb(target_path)

        if self.output:
            self.output.upload(target_path, tile_info)

    def generate_hillshade_tiles(self, tile_infos: Iterable[TileInfo],
                                 passes: dict[str, gdal.DEMProcessingOptions] = None) -> None:
        def generate_with_args(tile_info: TileInfo):
            self.generate_hillshade_tile(tile_info, passes)

        return self.apply_for_all_tile_infos(tile_infos, generate_with_args)

    def apply_for_all_tile_infos(self, tile_infos: Iterable[TileInfo],
                                 tile_info_consumer: Callable[[TileInfo], None]) -> None:
        self.download_tiles()
        self.create_virtual_dataset()

        tile_infos_by_level = defaultdict(list)
        for tile_info in tile_infos:
            tile_infos_by_level[tile_info.zoom].append(tile_info)

        for level, tile_infos_of_level in tile_infos_by_level.items():
            logging.info(f"Generating tiles for level {level}")
            list(alive_it(self.thread_pool.imap_unordered(tile_info_consumer, tile_infos_of_level),
                          total=len(tile_infos_of_level)))
