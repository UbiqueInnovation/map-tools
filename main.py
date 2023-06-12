import logging

from elevation import ElevationSwitzerland

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationSwitzerland()
    layer.download_tiles()
    layer.create_virtual_dataset()
