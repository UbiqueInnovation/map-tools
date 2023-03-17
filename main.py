import logging

from elevation import ElevationZurich
from tiles import TileInfo

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationZurich()
    layer.generate(TileInfo(zoom=6, x=33, y=22).descendants(max_zoom=14))
