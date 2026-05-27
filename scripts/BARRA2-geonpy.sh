#!/bin/bash  

# This script is used to run the BARRA-2 to geonpy conversion script. 

# Use: 
# First generate urls.csv files for each variable using the BARRA-2 download script.
# Then run this script to download and convert the NetCDF files to geonpy format.
# The latter takes ~10 per variable, so a good one to distribute if possible.

# Note, there's a lot of standard output. Run as ./BARRA2-geonpy.sh $base_dir > BARRA2-geonpy.log 2>&1

base_dir=$1
if [ -z "$base_dir" ]; then
    echo "Error: base_dir is required."
    echo "Usage: $0 <base_dir>"
    exit 1
fi

python BARRA2-urls.py $base_dir

echo "Written csv files for each variable to $base_dir/<var>/<var>-urls.csv."  
echo "Now downloading and converting to geonpy format..."

for var in tas wsgsmax #pr evspsbl mrso 
do
    python BARRA2-geonpy.py $var --csv $base_dir/$var/$var-urls.csv --base-dir $base_dir --download-per-file
done

