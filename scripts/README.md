### Overview  

The scripts here are focussed on accessing data to generate `geonpy` files. 
 
There is also a script to translate legacy metadata files in `.geomata` (pickle) form to `JSON`: 
  
```bash
cd ~/geonpy_dir
python ~/geonpy/scripts/update-legacy-geometa.py
```

### Generating `geonpy` files 
 
The example here uses climate data generated as part of BARRA-2:  
* https://opus.nci.org.au/spaces/NDP/pages/338002591/BARRA2+Parameter+Descriptions  
* https://thredds.nci.org.au/thredds/catalog/catalogs/ob53/catalog.html  
* https://connectsci.au/es/article/75/3/ES25032/251923/The-Australian-regional-atmospheric-reanalysis 
  

A set of variables is defined in the script `BARRA2-geonpy.sh` which can be run to download these and translate the monthly source (netCDF) files into a `geonpy` file.   
  
```bash  
base_dir="BARRA-2" 
mkdir -p $base_dir
bash BARRA2-geonpy.sh $base_dir > BARRA2-geonpy.log 2>&1 
```  

Note that there is an extensive range of [variables](https://opus.nci.org.au/spaces/NDP/pages/338002591/BARRA2+Parameter+Descriptions) which could be used in addition. 