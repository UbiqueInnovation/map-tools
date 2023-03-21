from commons import TileOutput
from .swissalti3d import SwissAlti3d


class ElevationSwitzerland(SwissAlti3d):

    def __init__(self, high_res: bool = False, output: TileOutput = None):
        super().__init__(output)
        self.high_res = high_res

    @property
    def tile_list(self) -> str:
        return 'elevation_switzerland_50cm_tiles' if self.high_res else 'elevation_switzerland_2m_tiles'

    @property
    def local_path(self) -> str:
        return 'switzerland/all/50cm' if self.high_res else 'switzerland/all/2m'
