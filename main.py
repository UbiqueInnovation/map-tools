import logging

from elevation import ElevationZurich
from storage import R2Client
from tiles import TileInfo

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationZurich(output_bucket=R2Client().maps_dev)
    layer.generate(TileInfo(zoom=6, x=33, y=22).descendants(max_zoom=14))
