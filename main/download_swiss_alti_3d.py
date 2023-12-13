import logging

from elevation import SwissAlti3d

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)

    for high_res in [True, False]:
        SwissAlti3d(high_res=high_res).download_tiles()
