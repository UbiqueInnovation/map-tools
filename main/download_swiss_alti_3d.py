import logging

from elevation import ElevationSwitzerland

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    layer_switzerland = ElevationSwitzerland()
    layer_switzerland.download_tiles()
