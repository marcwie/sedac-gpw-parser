A collection of scipts to work with high resolution gridded population data from the Socioeconomic Data and Applications Center (sedac). This is work in progress and updated frequently.

# Design principle & objectives
- Be as light as possible on RAM (storing the entire dataset into RAM causes
    unexpected behaviour on low memory high performance clusters as well as my
    crappy old computer...)
- Develop a file format that reduces the amount of stored redundancy and
    consequently output file sizes
- Allow for output files to be versioned with git (or similar). Thus the choice
    of using plain text output files

# Usage

1. Create an account at https://urs.earthdata.nasa.gov/ and keep logged in (otherwise you won't be able to download data).

1. Download the following file containing information on the grid:
https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-national-identifier-grid-rev11/gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip

2. Extract the data into the working directory ("./")

2. Use `create_file_index.py` to check which countries are present in each of the eight files

1. Use `create_per_country_file_lookup.py` to find the relevant entries in the
   data tables (stored in each of the 8 original input files) for every
   country. The script saves them as a `.txt`-file with custom format, e.g.
   
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
    
    - The first entry is the id of the corresponding input file
    - The second entry is the line number that contains relevant data (starting from 0 after the file header)
    - All following entries are pairs of lower (inclusive) and upper bounds (exclusive) for ranges of column numbers. For example `1,3 6,7, 8,10` would correspond to column numbers `1,2,6,8,9`.
