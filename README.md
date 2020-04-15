A package for working with high resolution gridded population data from the Socioeconomic Data and Applications Center (sedac). The package already works well but is still work in progress and updated frequently.

Information on the input data, i.e., the gridded global population count, is found here: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-population-count-rev11

Information on the corresponding grid that provides information on which country is contained in each grid cell is found here: https://sedac.ciesin.columbia.edu/data/set/gpw-v4-national-identifier-grid-rev11

Note that for now the package only parses the most recent 2020 estimates even though estimates for the years 2000, 2005, 201 and 2015 are available as well.

# Requirements

A few system-wide packages are required for this package to work (this is due to the depence on `cartopy` that allows to plot the data on a map). For Ubuntu you should type `sudo apt-get install libgeos-dev libproj-dev g++ python3-dev`.

For other operating systems and linux flavours please do `pip install cartopy` before installing `sedac-gpw-parser` and make sure that `cartopy` is installed correctly.

To properly download and prepare the data you need to have `unzip` installed. This can be done in Ubuntu by typing `sudo apt-get install unzip`.

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

    `download-sedac-gpw-data.sh` downloads the necessary data and stores them in a special folder `.sedac_gpw_parser` in your home directory. That way you can access the data from anywhere. The script prompts for your EarthData login credentials. Note that the script temporarily writes your password in plain text to `~/.netrc` in your home folder. However, the file is removed right after the scripts succesfully exits or in case of a keyboard interrupt. 
    
    **Note**: In some cases `download-sedac-gpw-data.sh` has proven to be error prone. See [below](#known-issues) for how to retrieve the input files manually.

    `python -m "sedac_gpw_parser.run"` prepares the data for later use for each of the 245 countries that are present in the data-set. For each country it creates three files:
    
    - `$HOME/.sedac_gpw_parser/output/COUNTRYID_valid_indices.txt` that stores the rows and columns of the original input files (and their underlying grid) that contain information on the country specified by the corresponding `COUNTRY_ID`
    - `$HOME/.sedac_gpw_parser/output/COUNTRYID_poulation.txt` stores the total population at each valid grid cell
    - `COUNTRYID.png` shows the data on a map (all plots are put in a folder `plots` in your `workdir`)
    
    Usually you do not need to worry about the first two output files. They just live in your `home` folder and you can access them by using the classes `Grid` and `Population` that are provided with this package. You can specify alternative locations for these output files when initializing `Grid` or `Population` (see the docstrings in `grid.py` and `population.py` for details).

3. If you want to work with the population data by, e.g., doing further analysis and evaluation, you can get a 2d `numpy` array of the data and the ranges of covered latitudes and longitudes by using the following snippet:
    ```python
    from sedac_gpw_parser import population
    pop = population.Population(country_id=250)
    population_array = pop.population_array()
    latitudes = pop.latitude_range()
    longitudes = pop.longitude_range()
    ```
    
4. Note that `country_id=250` in the above example returns the data for *France*. If you want to know the `id` of a certain country you can use 
    ```python
    from sedac_gpw_parser import utils
    utils.id_lookup("france")
    ```
    which generates the output:
    ```
    France : 250
    ```
    You can also do more fuzzy searches:
    ```python
    from sedac_gpw_parser import utils
    utils.id_lookup("unit")    
    ```
    which gives you:
    ```
    United Arab Emirates : 784
    United Kingdom of Great Britain and Northern Ireland : 826
    United Republic of Tanzania : 834
    United States of America : 840
    United States Virgin Islands : 850
    United States Minor Outlying Islands : 908
    ```
    
4. If you want to plot the data for a specific country you can use the following snippet:
    ```python
    from sedac_gpw_parser import utils
    plt = plot.Plot(country_id=250)
    plt.plot()
    ```
    You can use `plt.plot(show=True)` instead of `plt.plot()` if you want to display the figure in a `jupyter notebook`.

# Known issues

1. For some reason the script `download-sedac-gpw-data.sh` has proven to be error prone on some systems. Instead of using the script you can prepare the raw input data like so:
    ```
    mkdir $HOME/.sedac_gpw_parser
    ```
    Then open your browser and log in to https://urs.earthdata.nasa.gov/. Don't close your browser and keep logged in.
    Follow the two links below to download the necessary input files:
    
    - https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-population-count-rev11/gpw-v4-population-count-rev11_2020_30_sec_asc.zip
    - https://sedac.ciesin.columbia.edu/downloads/data/gpw-v4/gpw-v4-national-identifier-grid-rev11/gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip
    
    Make sure to download both files into `$HOME/.sedac_gpw_parser`. 
    
    You should then be able to `cd` into `$HOME/.sedac_gpw_parser` and run `download-sedac-gpw-data.sh` to extract the files into the required structure. 
    
    You can also extract both `.zip`-files manually and confirm that the extracted file structure looks like so:
    ```
    $HOME/.sedac_gpw_parser/
    ├── gpw-v4-national-identifier-grid-rev11_30_sec_asc
    │   ├── gpw_v4_national_identifier_grid_rev11_30_sec_1.asc
    │   ├── gpw_v4_national_identifier_grid_rev11_30_sec_1.prj
    │   ├── ...
    │   └── gpw_v4_national_identifier_grid_rev11_lookup.txt
    ├── gpw-v4-national-identifier-grid-rev11_30_sec_asc.zip
    ├── gpw-v4-population-count-rev11_2020_30_sec_asc
    │   ├── gpw_v4_population_count_rev11_2020_30_sec_1.asc
    │   ├── gpw_v4_population_count_rev11_2020_30_sec_1.prj
    │   ├── ...
    └── gpw-v4-population-count-rev11_2020_30_sec_asc.zip
    ```
    Most tools for unarchiving create such a directory structure automatically by extracting files into a folder with the same name as the `.zip`-archive.
    
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

    The first line is a header. In each following line:
    
    - The first entry is the id of the corresponding input file (between 1 and 8)
    - The second entry is the line number that contains relevant data (starting from 0 after the file header)
    - All following entries are pairs of lower (inclusive) and upper bounds (exclusive) for ranges of column numbers. For example `1,3 6,7, 8,10` would correspond to column numbers `1,2,6,8,9`.
    
    Hence for the example above, the line `4 5706 4873,4895` means that the file `gpw_v4_population_count_rev11_2020_30_sec_4.asc` contains relevant population data for the country with id `COUNTRYID` in row 5706 and columns 4873 to 4894 (4895-1). 
    
2. `COUNTRY_ID_population.txt` has the following custom format:
        
        ncols 880
        nrows 1780
        llcrnrlon 102.14166666666557
        llcrnrlat 8.56666666666699
        cellsize 0.0083333333333333
        NOTINCOUNTRY_value -2
        NODATA_value -1
        381x-2.0 1x125.026 498x-2.0
        377x-2.0 1x114.891 1x122.275 1x130.712 1x130.297 1x135.221 1x133.586 497x-2.0
        ...
        322x-2.0 1x20.37 1x39.449 1x40.073 1x5.32 554x-2.0

    The first 7 lines are the header. They describe:
    - The longitudinal extent of the data, i.e., the number of grid-cells or pixel
      in longitudinal direction.
    - The latitudinal extent of the data, i.e., the number of grid-cells or pixel
      in latitudinal direction.
    - The longitudinal position of the lower left corner of the image and, hence,
      also the lower left corner of of the lower left pixel.
    - The latitudinal position of the lower left corner of the image and, hence,
      also the lower left corner of of the lower left pixel.
    - The pixel- or cellsize in both, latitudinal and longitudinal, directions
      (measured in radiants). For the 30 arc-second resolution this value should
      correspond to 1/120.
    - The value indicating if a pixel or grid-cell is outside the considered
      country (usually -2).
    - The value indicating if a pixel or grid-cell has no data but is located
      inside the considered country (usually -1).

    The following *nrows* lines hold the data in a compressed format. The line
    ```
    381x-2.0 1x125.026 498x-2.0
    ```
    implies that the corresponding row of a decompressed array holds 381 times a
    `-2`, 1 time a `125.026` and then again 498 times a `-2`. The number of multipliers
    must equal the number of columns (`ncols` in the header). In this example we have
    `381+1+498=880=ncols`.
