import logging

from elevation import ElevationCentralSwitzerland

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layer = ElevationCentralSwitzerland()
    layer.download_tiles()
    layer.create_virtual_dataset()
