import logging

from elevation import Glo30

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dataset = Glo30()
    dataset.download_tiles()
    dataset.create_virtual_dataset()
