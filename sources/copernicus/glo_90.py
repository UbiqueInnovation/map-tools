from typing import Iterable

from ..source import Source


class Glo90Source(Source):

    @property
    def local_path(self) -> str:
        return 'global/glo90'

    @staticmethod
    def tile_names() -> list[str]:
        with open('sources/copernicus/glo_90_tiles') as tile_list:
            return [t.strip() for t in tile_list.readlines()]

    @staticmethod
    def to_url(tile_name: str) -> str:
        """
        The basic file name is the following:

        Copernicus_DSM_COG_[resolution]_[northing]_[easting]_DEM

        [resolution]: resolution in arc seconds (not meters!), which is 10 for GLO-30, and 30 for GLO-90.

        [northing]: e.g. S50_00, decimal degrees where the decimal part is always 00.
            In original files, this is the northing of the center of the bottom-most pixels, while in our files,
            because we removed the bottom-most pixels, the center of the new bottom-most pixels is one pixel-length
            (resolution) away to north.

        [easting]: e.g. w125_00, decimal degrees where the decimal part is always 00.
             The easting of the center of the left-most pixels.
        """
        return f'https://copernicus-dem-90m.s3.amazonaws.com/{tile_name}/{tile_name}.tif'

    def get_urls(self) -> Iterable[str]:
        return [self.to_url(tile_name) for tile_name in self.tile_names()]
