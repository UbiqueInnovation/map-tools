import logging

from sources import ZurichSource, SwitzerlandSource, Glo90Source

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    ZurichSource().download_tiles()
    SwitzerlandSource().download_tiles()
    Glo90Source().download_tiles()

    # Command line tools to post-process
    # gdal_merge.py -o merged/uzh.tif *.tif -a_nodata 0
    # gdalwarp merged.tif webmercator.tif -t_srs EPSG:3857
