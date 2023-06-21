from .swissalti3d import SwissAlti3d


class ElevationZurich(SwissAlti3d):
    @property
    def tile_list(self) -> str:
        return "elevation_zurich_tiles"

    @property
    def local_path(self) -> str:
        return "switzerland/zurich"
