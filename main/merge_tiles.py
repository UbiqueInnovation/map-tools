import numpy as np
from PIL import Image
from osgeo_utils.auxiliary.extent_util import Extent
from osgeo_utils.gdal_calc import Calc
from osgeo.gdal import Translate, Info


def merge(file_a, file_b, vertical=False):
    intersected = "intersected.tif"
    Calc(
        calc="A[0]",
        extent=Extent.INTERSECT,
        overwrite=True,
        outfile=intersected,
        A=[file_a, file_b],
    )
    rows, cols = Image.open(intersected).getbbox()[-2:][::-1]

    gradient_array = (
        np.tile(np.linspace(0.0, 1.0, rows), (cols, 1)).transpose()
        if vertical
        else np.tile(np.linspace(0.0, 1.0, cols), (rows, 1))
    )

    gradient_no_geo_tif = "gradient.no_geo.tif"
    gradient_tif = "gradient.tif"
    Image.fromarray(gradient_array).save(gradient_no_geo_tif)
    info = Info(intersected)
    print(info)
    Translate(destName=gradient_tif, srcDS=gradient_no_geo_tif, aSRS=info.Srs)

    Calc(
        calc="A * G + B * (1 - G)",
        extent=Extent.INTERSECT,
        overwrite=True,
        outfile="out.tif",
        A=file_a,
        B=file_b,
        G=gradient_tif,
    )


if __name__ == "__main__":
    merge("x0_y0.tif", "x0_y1.tif", vertical=True)


"""

gdal_calc.py -A overlap_20k_x1_y0.tiff -A overlap_20k_x0_y0.tiff --type=Float64 --outfile=overlap_20k_y0.tif --extent=intersect --overwrite --calc="numpy.average(A, axis=0)" 
gdal_calc.py -A overlap_20k_x1_y1.tiff -A overlap_20k_x0_y1.tiff --type=Float64 --outfile=overlap_20k_y1.tif --extent=intersect --overwrite --calc="numpy.average(A, axis=0)" 

gdal_calc.py -A overlap_20k_y0.tif --outfile=gradient_y0.tif --overwrite --calc="numpy.tile(numpy.linspace(0.0, 1.0, A.shape[1]), (A.shape[0], 1))" 
gdal_calc.py -A overlap_20k_y1.tif --outfile=gradient_y1.tif --overwrite --calc="numpy.tile(numpy.linspace(0.0, 1.0, A.shape[1]), (A.shape[0], 1))" 


gdal_calc.py -A overlap_20k_x1_y0.tiff -B overlap_20k_x0_y0.tiff -G gradient_y0.tif --outfile=overlap_20k_y0.tif --extent=intersect --overwrite --calc="A * G + B * (1 - G)" 
gdal_calc.py -A overlap_20k_x1_y1.tiff -B overlap_20k_x0_y1.tiff -G gradient_y1.tif --outfile=overlap_20k_y1.tif --extent=intersect --overwrite --calc="A * G + B * (1 - G)" 


gdal_merge.py -o overlap_20k_y0.merged.tif overlap_20k_x1_y0.tiff overlap_20k_x0_y0.tiff overlap_20k_y0.tif
gdal_merge.py -o overlap_20k_y1.merged.tif overlap_20k_x1_y1.tiff overlap_20k_x0_y1.tiff overlap_20k_y1.tif



gdal_calc.py -A overlap_20k_y0.merged.tif -A overlap_20k_y1.merged.tif --type=Float64 --outfile=overlap_20k.tif --extent=intersect --overwrite --calc="numpy.average(A, axis=0)" 

gdal_calc.py -A overlap_20k.tif --outfile=gradient.tif --overwrite --calc="numpy.tile(numpy.linspace(0.0, 1.0, A.shape[0]), (A.shape[1], 1)).transpose()" 

gdal_calc.py -A overlap_20k_y0.merged.tif -B overlap_20k_y1.merged.tif -G gradient.tif --outfile=overlap_20k.tif --extent=intersect --overwrite --calc="A * G + B * (1 - G)" 

gdal_merge.py -o overlap_20k.merged.tif overlap_20k_y0.merged.tif overlap_20k_y1.merged.tif overlap_20k.tif



"""
