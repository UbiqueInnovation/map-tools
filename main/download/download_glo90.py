import logging

from datasets import Glo90

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dataset = Glo90()
    dataset.download()
    dataset.create_vrt()
