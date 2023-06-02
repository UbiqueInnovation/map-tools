from .swissalti3d import SwissAlti3d


class ElevationCentralSwitzerland(SwissAlti3d):

    @property
    def tile_list(self) -> str:
        return 'elevation_central_switzerland_tiles'

    @property
    def local_path(self) -> str:
        return 'switzerland/central'
