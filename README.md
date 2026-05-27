Geonpy
======

Fast indexing of large spatio-temporal ND arrays for multiple time points.  

  
### Install  
  
```bash
pip install -e .
```  

### Use   

The main use of this module is to support the ObsPair GDM approach which builds "windows" of climatologies or weather windows leading up to the year a species observation was made. It does this by generating cubes of data as numpy memory mapped `geonpy` arrays.  

Generating `geonpy` arrays can be done presently by either pointing to a directory of raster files locally, or downloading netCDF files from a remote source. The python methods are here:   

```python 
from geonpy import concat_rasters_to_geonpy, concat_netcdf_to_geonpy 
```  

An example workflow to generate `geonpy` files from a remote source is given in the [scripts](scripts/) folder. 



