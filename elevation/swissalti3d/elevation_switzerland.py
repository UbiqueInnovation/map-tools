from mypy_boto3_s3.service_resource import Bucket

from .swissalti3d import SwissAlti3d


class ElevationSwitzerland(SwissAlti3d):

    def __init__(self, high_res: bool = False, output_bucket: Bucket = None):
        super().__init__(output_bucket)
        self.high_res = high_res

    @property
    def tile_list(self) -> str:
        return 'elevation_switzerland_50cm_tiles' if self.high_res else 'elevation_switzerland_2m_tiles'

    @property
    def local_path(self) -> str:
        return 'switzerland/all/50cm' if self.high_res else 'switzerland/all/2m'
