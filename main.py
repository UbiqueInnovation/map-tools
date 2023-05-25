import logging

from elevation import ElevationSwitzerland

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationSwitzerland(high_res=True)
    layer.download_tiles()
