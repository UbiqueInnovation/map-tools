import logging

from elevation import ElevationZurich

if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    layers = [
        ElevationZurich(),
    ]

    logging.info(f"Processing tiles for {list(map(str, layers))}")

    for layer in layers:
        layer.download_tiles()
        layer.merge_tiles()
        layer.warp_to_webmercator()

    # Command line tools to post-process
    # gdal_merge.py -o merged/uzh.tif *.tif -a_nodata 0
    # gdalwarp merged.tif webmercator.tif -t_srs EPSG:3857
    # gdalwarp -te 939258 5987771  978394 6026907 -ts 512 512 -t_srs EPSG:3857  merged.tif cut.tif
