import logging

from datasets import SwissAlti3d

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    for high_res in [False, True]:
        dataset = SwissAlti3d(high_res=high_res)
        dataset.download()
        dataset.create_vrt()
