from .swissalti3d_source import SwissAlti3dSource


class SwitzerlandSource(SwissAlti3dSource):

    def __init__(self, high_res: bool = False):
        self.high_res = high_res

    @property
    def tile_list(self) -> str:
        return 'switzerland_50cm_tiles' if self.high_res else 'switzerland_2m_tiles'

    @property
    def local_path(self) -> str:
        return 'switzerland/all/50cm' if self.high_res else 'switzerland/all/2m'
