import logging

from datasets import SwissSurface3dRaster

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dataset = SwissSurface3dRaster()
    dataset.download()
    dataset.create_vrt()
