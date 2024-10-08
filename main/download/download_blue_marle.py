import logging

from osgeo import gdal

from datasets.blue_marble import BlueMarble

if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    gdal.UseExceptions()

    dataset = BlueMarble()
    dataset.download()
    dataset.add_geo_reference()
    dataset.create_vrt()
