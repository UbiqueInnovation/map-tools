import logging
import os
from collections import defaultdict
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Iterable, Callable, Sequence, Optional

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from alive_progress import alive_it
from osgeo import gdal

from commons import TileOutput
from datasets import Dataset, TileSet
from tiles import TileInfo


class ElevationTools:
    # Set up thread pool
    num_threads = cpu_count()
    thread_pool = ThreadPool(num_threads)

    # Set environment variables for GDAL
    os.environ["GDAL_PAM_ENABLED"] = "NO"
    os.environ["GDAL_MAX_DATASET_POOL_SIZE"] = f"{num_threads}"

    # Configure gdal
    gdal.UseExceptions()

    @staticmethod
    def warp_to_tile(
        tile_info: TileInfo,
        source: Dataset,
        target_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        resolution: int = 512,
        overwrite_existing: bool = False,
        src_nodata: Optional[float] = None,
        cutline: Optional[str] = None,
        resample_alg: Optional[str] = None,
        creation_options: Optional[dict] = None,
    ) -> None:
        logging.debug(f"Cut and warp for tile {tile_info}")

        if os.path.exists(target_path):
            if overwrite_existing:
                os.remove(target_path)
            else:
                logging.debug(f"Skipping warping for tile {tile_info}.")
                return

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        gdal.Warp(
            destNameOrDestDS=target_path,
            srcDSOrSrcDSTab=source.path,
            options=gdal.WarpOptions(
                dstSRS=tile_info.srs,
                width=width or resolution,
                height=height or resolution,
                resampleAlg=resample_alg or "bilinear",
                outputBounds=tile_info.bounds_min_x_min_y_max_x_max_y,
                srcNodata=src_nodata,
                cutlineDSName=cutline,
                multithread=True,
                creationOptions=creation_options,
            ),
        )
        logging.debug(f"Warped tile {tile_info}.")

    @staticmethod
    def hillshade(
        source_path: str,
        target_path: str,
        options: gdal.DEMProcessingOptions = None,
    ):
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        gdal.DEMProcessing(
            destName=target_path,
            srcDS=source_path,
            processing="hillshade",
            options=options or gdal.DEMProcessingOptions(computeEdges=True, igor=True),
        )

    @staticmethod
    def image_to_rgb(path: str) -> None:
        Image.open(path).convert("RGBA").save(path)

    @staticmethod
    def multiply_images(paths: Sequence[str]) -> Image:
        if len(paths) == 1:
            return Image.open(paths[0])
        else:
            return ImageChops.multiply(
                Image.open(paths[0]), ElevationTools.multiply_images(paths[1:])
            )

    @staticmethod
    def adjust_image(
        source: str,
        target: str,
        brightness: float = 1,
        contrast: float = 1,
        gamma: float = 1,
    ) -> None:
        source_image = Image.open(source).convert("RGBA")
        brightness_adjusted = ImageEnhance.Brightness(source_image).enhance(brightness)
        gamma_adjusted = ElevationTools.adjust_gamma(brightness_adjusted, gamma)
        contrast_adjusted = ImageEnhance.Contrast(gamma_adjusted).enhance(contrast)
        contrast_adjusted.save(target)

    @staticmethod
    def adjust_gamma(image: Image, gamma: float) -> Image:
        inv_gamma = 1.0 / gamma
        table = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]
        ).astype("uint8")
        return Image.fromarray(cv2.LUT(np.asarray(image), table))

    @staticmethod
    def generate_hillshade_tiles(
        dataset: Dataset,
        tile_infos: Iterable[TileInfo],
        target: TileSet = None,
        options: gdal.DEMProcessingOptions = None,
        passes: dict[str, gdal.DEMProcessingOptions] = None,
        output: TileOutput = None,
    ) -> None:
        target = target or dataset.hillshade

        def generate_hillshade_tile(tile_info: TileInfo) -> None:
            warped_path = dataset.warped.tile_path(tile_info)
            ElevationTools.warp_to_tile(
                tile_info, source=dataset, target_path=warped_path
            )
            if passes:
                for key, arguments in passes.items():
                    target_base_path = f"{target.tile_base_path(tile_info)}_{key}"
                    target_path = f"{target_base_path}.png"
                    ElevationTools.hillshade(
                        warped_path, target_path, arguments["options"]
                    )
                    ElevationTools.adjust_image(
                        target_path,
                        f"{target_base_path}_adjusted.png",
                        **arguments.get("corrections", dict()),
                    )

                paths = [
                    f"{target.tile_base_path(tile_info)}_{key}_adjusted.png"
                    for key in passes.keys()
                ]
                ElevationTools.multiply_images(paths).save(target.tile_path(tile_info))

            else:
                ElevationTools.hillshade(
                    warped_path, target.tile_path(tile_info), options
                )
                ElevationTools.image_to_rgb(target.tile_path(tile_info))

            if output:
                output.upload(target.tile_path(tile_info), tile_info)

        return ElevationTools.apply_for_all_tile_infos(
            tile_infos, generate_hillshade_tile
        )

    @staticmethod
    def generate_color_relief_tiles(
        dataset: Dataset,
        tile_infos: Iterable[TileInfo],
        color_filename: str,
        output: TileOutput = None,
    ) -> None:
        def generate_color_relief_tile(tile_info: TileInfo):
            warped_tile_path = dataset.warped.tile_path(tile_info)
            ElevationTools.warp_to_tile(tile_info, dataset, warped_tile_path)

            target_path = dataset.color_relief.tile_path(tile_info)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            gdal.DEMProcessing(
                destName=target_path,
                srcDS=warped_tile_path,
                processing="color-relief",
                options=gdal.DEMProcessingOptions(
                    colorFilename=color_filename, addAlpha=True
                ),
            )

            if output:
                output.upload(target_path, tile_info)

            os.remove(target_path)
            os.remove(warped_tile_path)

        return ElevationTools.apply_for_all_tile_infos(
            tile_infos, generate_color_relief_tile
        )

    @staticmethod
    def generate_tiles_for_image(
        dataset: Dataset,
        tile_infos: Iterable[TileInfo],
        target: TileSet,
        output: TileOutput = None,
        src_nodata: Optional[float] = None,
        cutline: Optional[str] = None,
        remove_after_upload: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
        resample_alg: Optional[str] = None,
        creation_options: Optional[dict] = None,
    ) -> None:
        def generate_tile_for_image(tile_info: TileInfo):
            target_path = target.tile_path(tile_info)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            ElevationTools.warp_to_tile(
                tile_info,
                source=dataset,
                target_path=target_path,
                overwrite_existing=True,
                src_nodata=src_nodata,
                cutline=cutline,
                height=height,
                width=width,
                resample_alg=resample_alg,
                creation_options=creation_options,
            )

            if target.file_extension == "png":
                ElevationTools.image_to_rgb(target_path)

            if target.file_extension in ["jpg", "jpeg"]:
                Image.open(target_path).convert("RGB").save(target_path)

            if output:
                output.upload(target_path, tile_info)

            if remove_after_upload:
                os.remove(target_path)

        return ElevationTools.apply_for_all_tile_infos(
            tile_infos, generate_tile_for_image
        )

    @staticmethod
    def apply_for_all_tile_infos(
        tile_infos: Iterable[TileInfo],
        tile_info_consumer: Callable[[TileInfo], None],
    ) -> None:
        tile_infos_by_level = defaultdict(list)
        for tile_info in tile_infos:
            # noinspection PyUnresolvedReferences
            tile_infos_by_level[tile_info.zoom].append(tile_info)

        for level, tile_infos_of_level in sorted(tile_infos_by_level.items()):
            logging.info(f"Generating tiles for level {level}")
            apply_function = ElevationTools.thread_pool.imap_unordered(
                tile_info_consumer, tile_infos_of_level
            )
            # noinspection PyTypeChecker
            list(alive_it(apply_function, total=len(tile_infos_of_level)))
