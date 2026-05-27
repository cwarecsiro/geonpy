import os
import sys

import pandas as pd

""" 
Generate CSVs of URLs for BARRA-2 data variables. 

Use: 
cd ~/geonpy_dir
python ~/geonpy/scripts/BARRA2-geonpy.py BARRA-2
"""

variables = [
    "hurs","tas","uas",
    "vas","wsgsmax","pr",
    "evspsbl","evspsblpot","sftlf",
    "mrso","tsl","netrad"
]
base_url = "https://thredds.nci.org.au/thredds/fileServer/ob53/output/reanalysis/" 
res = "AUST-04"
product = "BARRA-C2"
freq = "mon"


if __name__ == "__main__":
    dstdir=sys.argv[1] 
    os.makedirs(dstdir, exist_ok=True)
    
    for var in variables:
        var_dst = f"{dstdir}/{var}"
        os.makedirs(var_dst, exist_ok=True)
        urls = []
        for year in range(1979, 2026):
            for month in range(1, 13):
                timepoint = f"{year}{month:02d}-{year}{month:02d}"
                url = f"{base_url}/{res}/BOM/ERA5/historical/hres/{product}/v1/{freq}/{var}/latest/{var}_{res}_ERA5_historical_hres_BOM_{product}_v1_{freq}_{timepoint}.nc"
                urls.append(url)
        urls = pd.DataFrame(urls)
        urls.to_csv(f"{var_dst}/{var}-urls.csv", index = False)