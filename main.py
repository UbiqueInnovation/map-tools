import logging

from osgeo import gdal

from commons import TileOutput, R2Client
from elevation import ElevationSwitzerland
from tiles import WebmercatorTileInfo

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationSwitzerland(output=TileOutput(R2Client().maps_dev, "tiles/v1/hillshade/test"))
    layer.generate_hillshade_tiles(WebmercatorTileInfo(zoom=6, x=33, y=22).descendants(max_zoom=12), passes={
        "40deg": dict(
            options=gdal.DEMProcessingOptions(altitude=45, azimuth=40, zFactor=1.7, computeEdges=True),
            corrections=dict(brightness=2.1, contrast=1, gamma=7)
        ),
        "330deg": dict(
            options=gdal.DEMProcessingOptions(altitude=45, azimuth=330, zFactor=1.7, computeEdges=True),
            corrections=dict(brightness=2, contrast=1, gamma=5)
        ),
    })
