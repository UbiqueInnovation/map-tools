# Map Tools

Collection of tools, for various map related issues. 

## Digital Elevation Map

This repository includes scripts for downloading and processing digital elevation maps. 

```python
from sources import ZurichSource, SwitzerlandSource, Glo90Source

# Downloading the tiles
ZurichSource().download_tiles()
SwitzerlandSource().download_tiles()
Glo90Source().download_tiles()
```

### SwissAlti3D

The data can be found here: [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html)

### Copernicus Digital Elevation Model datasets

The data canbe found here: [Tile list](https://copernicus-dem-30m.s3.amazonaws.com/tileList.txt)
