import logging

from datasets import Glo30

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    dataset = Glo30()
    dataset.download()
