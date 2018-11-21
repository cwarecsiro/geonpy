#!/usr/bin/env python3
"""
Geonpy class
============
Provides a way to read in non-contiguous elements (points) from a 3(4?)D array on disk.

Purpose 
-------
Geared towards providing a means to 'extract' values from multiple rasters to enable dynamic gdm table builds.  
This is achieved by reading array element values directly from disk using mumpy memmaps.  

Limitations
-----------
- Other existing file types (e.g. hdf5) might be better suited generally (though array manipulations may not be as straghtforward). 
- tiffile library can probably achieve this to and may be even better suited.  
"""
import struct, rasterio, json, pickle
import numpy as np
from affine import Affine
from rasterio.crs import CRS
import feather

__version__ = "0.01"

def load_npy_to_memmap(filename, dtype, shape):
    """Generate a memory map of an array on disk."""
    # doesn't cope with files written by concat_rasters_to_geonpy
    # I must be mashing the header somehow
    with open(filename, 'rb') as f:
        magic = f.read(6)
        version = f.read(1)
        # Get the header length as a 2-byte short int.
        header_len = struct.unpack('>H', f.read(2))[0]
        data = np.memmap(filename, dtype=dtype, mode='r', shape=shape, offset=6+2+2+header_len)
    return(data)
    
def transform_from_bounds(west, south, east, north, width, height):
    """Return an Affine transformation given bounds, width and height."""
    return Affine.translation(west, north) * Affine.scale(
        (east - west) / width, (south - north) / height)

def xy2rc(xy, transform, op = np.floor):
    """For a given set of coordinates, return the row and column from an array.
    
    Parameters
    ----------
    xy: ndarray or DataFrame, required
    transform: Affine transform, required
    op: numpy operation, optional 
        operation to convert transformation of xy into integers. Default np.floor
        
    Returns
    -------
    row, col (int)
    """
    xy = np.array(xy)
    fcol, frow = ~transform * xy.T
    frow = np.floor(frow).astype(int)
    fcol = np.floor(fcol).astype(int)
    return(frow, fcol)

class Geonpy(object):
    """Geonpy class to enable reading individual cells of a raster from disk"""
    def __init__(self, arr, bounds = None, nodata = None, meta = None, crs = None, bands = None):
        self.src = None
        self.array = None
        self.bounds = None
        self.nodata = None
        self.meta = None
        self.crs = None
        self.nbands = None
        self.shape = None
        
        if isinstance(arr, np.ndarray):
            if bounds:
                self.bounds = bounds
            elif meta:
                bounds = meta['bounds']
                self.bounds = bounds
            else:
                print('Need array geospatial bounds object to create transform')
                return
            self.array = arr
            self.shape = arr.shape
            if nodata is None:
                if meta is None:
                    nodata = -9999
                else:
                    nodata = meta['nodata']
            self.nodata = nodata
            if bands is None:
                if len(arr.shape) > 2:
                    self.nbands = arr.shape[-1] # assumes 3rd dim is bands
                else:
                    self.nbands = 1
            else:
                self.nbands = bands
            self.dtype = arr.dtype
            self.shape = arr.shape
            
            if not meta:
                meta = {}
                meta['height'] = arr.shape[0]
                meta['width'] = arr.shape[1]
                meta['dtype'] = arr.dtype
                meta['count'] = self.nbands
                
                w, s, e, n = bounds
                transform = transform_from_bounds(w, s, e, n, arr.shape[1], arr.shape[0])
                meta['transform'] = transform
                
                if crs is not None:
                    meta['crs'] = crs
                
        else:
            geometa = '{}.geometa'.format(arr.split('.')[0])
            try:
                with open(geometa, 'rb') as gm: 
                    #gm.seek(0)
                    meta = pickle.load(gm)
            except FileNotFoundError:
                print('Expected to find {}.geometa, but the file does not exist'.format(geometa))
                return
            
            self.src = arr
            self.meta = meta
            self.nbands = meta['count']
            
            # get shape and dtype from header
            # shape, _, dtype = read_header(arr)
            # actually, read_header is broken when used on npy files written by
            # concat_rasters_to_geonpy, so have to wing it a bit:
            # if it's a 2D array, it must only have two dims on disk... 
            if meta['count'] == 1:
                shape = (meta['height'], meta['width'])
            else:
                shape = (meta['height'], meta['width'], meta['count'])
            self.shape = shape
            # self.array = load_npy_to_memmap(self.src, dtype=dtype, shape = shape)
            self.array = np.memmap(self.src, dtype=self.meta['dtype'], mode='r', shape=self.shape)
                        
            transform = meta['transform']
            w, n = transform.xoff, transform.yoff
            e, s = transform * (shape[1], shape[0])
            self.bounds = w, s, e, n
       
    def write_meta(self):
        """Writes a binary metadata file"""
        dst = '{}.geometa'.format(self.src.split('.')[0])
        with open(dst, 'wb') as output:
            pickle.dump(self.meta, output)
    
    def read_points(self, pts, dim_idx = None):
        """Read individual points given as coordinates from an array.
        
        Parameters
        ----------
        pts: path to CSV file or feather file or ndarray or DataFrame, required
            The data is expected to be provided in two columns as long, lat.
            No safety provided. 
        dim_idx: ndarray, optional
            If supplied, used to index the 3rd dim of the ndarray. Defaults to all. 
            
        Returns
        -------
        ndarray with a column for each dimension of the array providing the source values. 
        
        """
        if not isinstance(pts, np.ndarray):
            if isinstance(pts, str):
                if pts[-4:] == '.csv':
                    try:
                        pts = pd.read_csv(pts)
                    except FileNotFoundError:
                        print('Looks like {} is a file but pandas cannot read it as a .CSV'.format(pts))
                        return
                else:
                    try:
                        pts = feather.read_dataframe(pts)
                    except FileNotFoundError:
                        print('Looks like {} is a feather file but feather cannot read it'.format(pts))
                        return
        ridx, cidx = xy2rc(pts, self.meta['transform'])
        if len(self.shape) > 2:
            if dim_idx is not None:
                if len(dim_idx.shape) == 2:
                    ridx = ridx.reshape(ridx.shape[0], 1)
                    cidx = cidx.reshape(cidx.shape[0], 1)
                    arr = self.array[ridx, cidx, dim_idx]
                    return(arr)
                else:
                    return(self.array[ridx, cidx, dim_idx])
            else:
                return(self.array[ridx, cidx, :])
        else:
            return(self.array[ridx, cidx])
            
    def write_geonpy(self, dst):
        np.save(self.array, dst)
        dst = '{}.geometa'.format(self.src.split('.')[0])
        with open(dst, 'wb') as output:
            pickle.dump(self.meta, output)     
    
    def read_header(filename):
        with open(filename, 'rb') as fhandle:
            major, minor = np.lib.format.read_magic(fhandle)
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(fhandle)
            return(shape, fortran, dtype)
    
    def concatenate(dst, header):
        with open(dst, 'wb') as f:
            fmt.write_array_header_2_0(f, header)
            for fname in input_fnames:
                m = np.load(fname)
                f.write(m.tostring('C'))
                
def concat_rasters_to_geonpy(dst, input_filepaths):
    """Read rasters and sink them to an ND array on disk as a Geonpy thing.
    
    Parameters
    ----------
    dst: filepath, required.
        Location to write file to. File extension (.npy) not required.
    input_filepaths: filepaths (list), required
        Locations of raster files to concatenate to a Geonpy file.
        
    Notes
    -----
    Reads rasters in a loop, so may not provide great speed, but it's easy on memory.
    """
    template = sp.Raster(input_filepaths[0])
    meta = template.meta
    template = template.read().array
    h, w, = template.shape
    d = len(input_filepaths)
    
    # create mm
    mm = np.memmap(dst, dtype=template.dtype, mode='w+', shape=(h, w, d))
    for f in range(len(input_filepaths)):
        mm[:,:,f] = sp.Raster(input_filepaths[f]).read().array
    del mm
    
    # format and write meta
    opts = ['height', 'width', 'dtype', 'transform', 'crs', 'count']
    sub_meta = meta.copy()
    sub_meta['count'] = d
    for key in meta.keys():
        if key not in opts:
            del sub_meta[key]
    dst = '{}.geometa'.format(dst.split('.')[0])
    with open(dst, 'wb') as output:
        pickle.dump(sub_meta, output)

def gen_multi_index_slice(year_mon, window, st_year = None, st_mon = None):
    """
    Create 2D array of time slice (monthly) indexes as a look-up input
    
    Parameters
    ----------
    year_mon: array, required
        2D array with year and month as cols, both as integer.
    window: int, required
        length of climate window in years
    st_year: int, optional
        starting year of corresponding geonpy. Default 1990.
    st_mon: int, optional
        starting mon of corresponding geonpy. Default 1.
    
    Returns
    -------
    2D numpy array with rows as geographic locations, and cols as monthly idx
    
    TODO
    ----
    This, and an upstream functon, are still is a bit loopy. Try and flatten these processes. 
    """
    if not st_year:
        st_year = 1900
    if not st_mon:
        st_mon = 1
    
    # convert year_mon to an int
    year = year_mon[:, 0]
    mon = year_mon[:, 1]
    st_slice = (((year-st_year) * 12) + mon) - (st_mon -1)
    
    # output
    z_idx = np.zeros((year_mon.shape[0], window)).astype(int)
    
    # loop over window
    z_idx[:, window-1] = st_slice
    for i in range(window-1):
        z_idx[:, i] = st_slice-(window-(i+1))
    
    return(z_idx)

def linidx_take(val_arr,z_indices):

    # Get number of columns and rows in values array
    _,nC,nR = val_arr.shape

    # Get linear indices and thus extract elements with np.take
    idx = nC*nR*z_indices + nR*np.arange(nR)[:,None] + np.arange(nC)
    return np.take(val_arr,idx) # Or val_arr.ravel()[idx]

def calc_climatology_window(arr, mstat, cstat):
    """Summarize timeseries window of months to a 'climatology.
    
    Parameters
    ----------
    arr: array, requrired
    mstat: np function, required
    cstat: np function, required
    
    Returns
    -------
    1D array?
    """
    cuts = arr.shape[1] / 12
    cuts = np.arange(0, arr.shape[1], 12).tolist()
    yearly = np.dstack([arr[:, i:i + 12] for i in cuts])
    yearly_stat = mstat(yearly, axis = 1)
    clim_stat = cstat(yearly_mean, axis = 1)
    
    # anything else?
    
    return(yearly_stat)