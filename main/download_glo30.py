import logging

from elevation import Glo30

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    Glo30().download_tiles()
