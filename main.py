import logging

from elevation import ElevationZurich, ElevationSwitzerland, Glo90

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layers = [ElevationZurich(), ElevationSwitzerland(), Glo90()]
    logging.info(f"Processing tiles for {layers}")

    logging.info("Loading tiles")
    for layer in layers:
        layer.download_tiles()

    logging.info("Merging tiles")
    for layer in layers:
        layer.merge_tiles()

    # Command line tools to post-process
    # gdal_merge.py -o merged/uzh.tif *.tif -a_nodata 0
    # gdalwarp merged.tif webmercator.tif -t_srs EPSG:3857
