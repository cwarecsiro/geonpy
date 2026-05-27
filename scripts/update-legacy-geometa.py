import glob 

from geonpy.geonpy import (
    LegacyCRSUnpickler, CRSProxy, serialize_meta,
    write_meta_json
)

"""
This script is used to update legacy .geometa files to use JSON instead of pickle. 
The script: 
* searches for all .geometa files in the current directory, 
* deserializes them using the LegacyCRSUnpickler, 
* replaces any CRSProxy objects with real CRS objects, 
* and then writes the updated metadata to a new .json file with the same name 
  (but with a .json extension). 
.geometa files are left unchanged.  

Use 
--- 
cd ~/geonpy_dir
python ~/geonpy/scripts/update-legacy-geometa.py
"""

if __name__ == '__main__':
    for file in glob.glob('*.geometa'):
        with open(file, "rb") as f:
            meta = LegacyCRSUnpickler(f).load()
            if "crs" in meta and isinstance(meta["crs"], CRSProxy):
                meta["crs"] = meta["crs"].to_crs()
        file_name = file.replace('.geometa', '.json')
        write_meta_json(meta, file_name)
        
       
