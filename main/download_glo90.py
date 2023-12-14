import logging

from elevation import Glo90

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dataset = Glo90()
    dataset.download_tiles()
    dataset.create_virtual_dataset()
