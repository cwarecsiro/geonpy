import sys
import glob
import argparse
from pathlib import Path
import pandas as pd

from geonpy.geonpy import concat_netcdf_to_geonpy    

"""
This script is used to generate `geonpy` files for BARRA-2 data variables. 
It can build the geonpy files from local NetCDF files, or from a CSV containing file paths or URLs, 
it will download remote files as needed and delete these after processing (by default).  

Use
--- 
var_name = "hurs" # e.g. "hurs"
base_dir = "BARRA-2" 
python ~/geonpy/scripts/BARRA2-geonpy.py \ 
    $var_name \
    --csv $base_dir/$var_name/$var_name-urls.csv \
    --base-dir $base_dir \  
    --download-per-file 
"""

base_dir = "BARRA-2"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE_TIF = REPO_ROOT / "data" / "aus-5km-template-uint8.tif"

def read_sources_from_csv(csv_path):
    """Read a CSV of URLs/paths from named column or fallback to first column."""
    df = pd.read_csv(csv_path)
    if df.empty:
        return []

    preferred = ["path", "filepath", "file", "url", "source"]
    lower_to_original = {str(col).strip().lower(): col for col in df.columns}
    chosen = None
    for name in preferred:
        if name in lower_to_original:
            chosen = lower_to_original[name]
            break

    if chosen is None:
        chosen = df.columns[0]

    series = df[chosen].dropna().astype(str).str.strip()
    series = series[~series.str.lower().isin(preferred)]
    series = series[series != ""]
    return series.tolist()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build geonpy cube from local NetCDF files or CSV of filepaths/URLs."
    )
    parser.add_argument("var_name", help="Variable name to extract from NetCDF files")
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Optional CSV containing source file paths or URLs",
    )
    parser.add_argument(
        "--template",
        dest="template_path",
        default=None,
        help=f"Optional template raster file path for geonpy cube. Defaults to {DEFAULT_TEMPLATE_TIF}",
    )
    parser.add_argument(
        "--base-dir",
        dest="base_dir",
        default=base_dir,
        help=f"Base directory for input NetCDF files or where to write geonpy to. Defaults to '{base_dir}'",
    )   
    parser.add_argument(
        "--download-per-file",
        action="store_true",
        help="Download each remote source into a temp file while processing",
    )
    parser.add_argument(
        "--keep-downloaded",
        action="store_true",
        help="Do not remove temporary downloaded files after processing",
    )
    parser.add_argument(
        "--download-dir",
        default=None,
        help="Directory for temporary downloads when --download-per-file is used",
    )
    args = parser.parse_args()

    
    target_var = args.var_name
    base_dir = args.base_dir
    var_dir = f"{base_dir}/{target_var}"
    if args.csv_path:
        var_src = read_sources_from_csv(args.csv_path)
    else:
        var_src = glob.glob(f"{var_dir}/*.nc")
        var_src.sort()

    if not var_src:
        raise ValueError("No NetCDF source files found. Check --csv input or local file pattern.")

    template_path = Path(args.template_path).expanduser() if args.template_path else DEFAULT_TEMPLATE_TIF
    if not template_path.exists():
        raise FileNotFoundError(f"Template raster file not found: {template_path}")

    concat_netcdf_to_geonpy(
        dst = f"{base_dir}/{target_var}/{target_var}.npy",
        input_filepaths = var_src, 
        var_name = target_var,
        template = str(template_path),
        download_per_file = args.download_per_file,
        cleanup_downloaded = not args.keep_downloaded,
        download_dir = args.download_dir
    )