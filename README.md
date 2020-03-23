A package for working with high resolution gridded population data from the Socioeconomic Data and Applications Center (sedac). The package already works well but is still work in progress and updated frequently.

Information on the input data, i.e., the gridded global population count, is found here: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11

Information on the corresponding grid that provides information on which country is contained in each grid cell is found here: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-national-identifier-grid-rev11

Note that for now the package only parses the most recent 2020 estimates even though estimates for the years 2000, 2005, 201 and 2015 are available as well.

# Requirements

A few system-wide packages are required for this package to work (this is due to the depence on `cartopy` that allows to plot the data on a map). For Ubuntu you should type `sudo apt-get install libgeos-dev libproj-dev`.

# Installation

This package only works with `python3`. To install just type:
```
git clone git@github.com:marcwie/sedac-gpw-parser.git
cd sedac-gpw-parser
python setup.py install
```

# Usage

1. Create an account at https://urs.earthdata.nasa.gov/ 

2. Create your working directory, download the necessary files and run the package like so:
    ```
    mkdir workdir
    cd workdir
    download-sedac-gpw-data.sh
    python -m "sedac_gpw_parser.run"
    ```

    `download-sedac-gpw-data.sh` downloads the necessary data. The script prompts for your EarthData login credentials. Note that the script temporarily writes your password in plain text to `~/.netrc` in your home folder. However, the file is removed right after the scripts succesfully exits or in case of a keyboard interrupt. 

    `python -m "sedac_gpw_parser.run"` prepares the data for later use for each of the 245 countries that are present in the data-set. For each country it creates three files:
    
    - `COUNTRYID_valid_indices.txt` that stores the rows and columns of the original input files (and their underlying grid) that contain information on the country specified by the corresponding `COUNTRY_ID`
    - `COUNTRYID_poulation.txt` stores the total population at each valid grid cell
    - `COUNTRYID.png` shows the data on a map

# Design principle & objectives
- Be as light as possible on RAM since storing the entire dataset into RAM is expected to cause
    trouble on high performance clusters (that usually have very low memory) and older hardware
- Develop a file format that reduces the amount of stored redundancy and
    consequently output file sizes while style being `python`-readible without using external compression algorithms
- Allow for output files to be versioned with git (or similar) or inspected by using common text editors. Thus the choice
    of using plain text output files

# Custom file format for output files

1. `COUNTRYID_valid_indices.txt` has the following custom format:
   
        #file_id, line_number, column_numbers
        1 2206 77,101
        1 2207 72,106 108,112 114,119
        1 2208 56,59 71,102 107,135
        1 2209 52,60 76,81 84,94 95,102 106,122 124,139 140,149
        ...
        4 5706 4873,4895
        4 5707 4873,4894
        4 5708 4874,4893
        4 5709 4875,4893
        4 5710 4876,4892

    The first line as a header. In each following line:
    
    - The first entry is the id of the corresponding input file (between 1 and 8)
    - The second entry is the line number that contains relevant data (starting from 0 after the file header)
    - All following entries are pairs of lower (inclusive) and upper bounds (exclusive) for ranges of column numbers. For example `1,3 6,7, 8,10` would correspond to column numbers `1,2,6,8,9`.
    
    Hence for the example above, the line `4 5706 4873,4895` means that the file `gpw_v4_population_count_rev11_2020_30_sec_4.asc` contains relevant population data for the country with id `COUNTRYID` in row 5706 and columns 4873 to 4894 (4895-1). 
