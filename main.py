import logging

from elevation import ElevationSwitzerland
from storage import R2Client, TileOutput
from tiles import TileInfo

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationSwitzerland(output=TileOutput(R2Client().maps_dev, base_path='tiles/v1/hillshade'))
    layer.generate(TileInfo(zoom=6, x=33, y=22).descendants(max_zoom=14))
