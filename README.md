A collection of scipts to work with high resolution gridded population data from the Socioeconomic Data and Applications Center (sedac). This is work in progress and updated frequently.

# Usage

1. Create an account at https://urs.earthdata.nasa.gov/ and keep logged in (otherwise you won't be able to download data).

1. Download the following file containing information on the grid:
https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-national-identifier-grid-rev11/gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip

2. Extract the data into the working directory ("./")

2. Use `create_file_index.py` to check which countries are present in each of the eight files
