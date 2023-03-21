import logging

from commons import R2Client, TileOutput
from elevation import Glo90
from tiles import TileInfo

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = Glo90(output=TileOutput(R2Client().maps_dev, base_path='tiles/v1/hillshade'))
    layer.generate(TileInfo(zoom=0, x=0, y=0).descendants(min_zoom=5, max_zoom=10))
