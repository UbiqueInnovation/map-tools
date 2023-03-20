# Map Tools

Collection of tools, for various map related issues.

## Digital Elevation Map

This repository includes scripts for downloading and processing digital elevation maps.

### Example

Generate elevation tiles for Switzerland

```python
from tiles import TileInfo
from elevation import ElevationSwitzerland

ElevationSwitzerland().generate(TileInfo(zoom=6, x=33, y=22).descendants(max_zoom=14))
```

### SwissAlti3D

The data can be found here: [swissALTI3D](https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html)

### Copernicus Digital Elevation Model datasets

The data canbe found here: [Tile list](https://copernicus-dem-30m.s3.amazonaws.com/tileList.txt)
