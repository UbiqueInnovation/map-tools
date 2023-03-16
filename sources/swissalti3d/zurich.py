from .swissalti3d_source import SwissAlti3dSource


class ZurichSource(SwissAlti3dSource):

    @property
    def tile_list(self) -> str:
        return 'zurich_tiles'

    @property
    def local_path(self) -> str:
        return 'switzerland/zurich'
