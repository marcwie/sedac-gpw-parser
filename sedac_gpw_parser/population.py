"""
Parse population data from the ASCII input files that are provided by the
Socioeconomic Data and Applications Center (sedac) and that have been
downloaded using download-sedac-gpw-data.sh.

Loads the ascii input files, crops the data to match a specified country and
stores the data in a custom space-saving file format for later use. Provides
functions to compress and decompress, i.e., load and save data to and from the
custom file format.

The data itself describes the population count per pixel.

An example data set in the custom file format reads like so:

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

381x-2.0 1x125.026 498x-2.0

Implies that the corresponding row of a decompressed array holds 381 times a
-2, 1 time a 125.026 and then again 498 times a -2. The number of multipliers
must equal the number of columns (ncols in the header). In this example we have
381+1+498=880=ncols.
"""
import os
import numpy as np
from sedac_gpw_parser.grid import Grid

POPULATION_FILE_NAME = "gpw_v4_population_count_rev11_2020_30_sec_{0}.asc"
POP_OUTPUT_FILE_NAME = "{0}_population.txt"
DATA_FOLDER = os.path.expanduser("~") + "/.sedac_gpw_parser/"

def _decompress(indices):
    """
    Convert a str representing a sequence of entries into a list.

    :param indices: One line in the custom input data that represents a
                    sequence of entries in a list. See module docstring for 
                    information on the file format.
    :type indices: str

    :returns: The decompressed list
    :rtype: list of float

    Examples:
    >>> _decompress("2x3.0 1x4.2 3x2.0")
    [3.0, 3.0, 4.2, 2.0, 2.0, 2.0]

    >>> _decompress("3x0 2x5 3x4")
    [0.0, 0.0, 0.0, 5.0, 5.0, 4.0, 4.0, 4.0]
    """ 
    decompressed = []
    for entry in indices.split(" "):
        if "x" in entry:
            counter, value = entry.split("x")
        else:
            counter = 1
            value = entry
        decompressed.extend(int(counter) * [float(value)])
    return decompressed


def _compress(array):
    """
    Convert a list or array into a str representing the sequence of elements.
   
    If the list contains integer and float values the compressed array may be
    expressed in terms of integers or floats depending on the type of the first
    occurence of a number (see the last two examples below for details). Since
    this function is only meant to be used in conjuction with the _decompress()
    function this behaviour does not make any difference as _decompress()
    always returns a list of floats.

    :param array: The uncompressed list
    :type array: 1d numpy array or list of int or float
       
    :returns: The compressed representation of the array as explained in the
              module docstring. 
    :rtype: str

    Examples:
    >>> _compress([3.0, 3.0, 4.2, 2.0, 2.0, 2.0])
    '2x3.0 1x4.2 3x2.0'

    >>> _compress([0, 0, 0, 5, 5, 4, 4, 4])
    '3x0 2x5 3x4'

    >>> _compress([0, 0.0, 0, 5, 5, 4, 4, 4])
    '3x0 2x5 3x4'

    >>> _compress([0.0, 0, 0, 5, 5, 4, 4, 4])
    '3x0.0 2x5 3x4'
    """
    indices = ""

    start = array[0]
    counter = 1
    for _ in range(1, len(array)):
        if array[_] == start:
            counter += 1
        else:
            indices += str(counter) + "x"+str(start) + " "
            start = array[_]
            counter = 1
    indices += str(counter) + "x"+str(start)

    return indices


class Population(Grid):
    

    def __init__(self, country_id, output_folder=DATA_FOLDER+"output/",
                 population_input_folder=DATA_FOLDER+"gpw-v4-population-count-rev11_2020_30_sec_asc/",
                 grid_input_folder=DATA_FOLDER+"gpw-v4-national-identifier-grid-rev11_30_sec_asc/",
                 overwrite=False):

        assert not overwrite, "Not implemented yet!"

        pop_output_file_name = POP_OUTPUT_FILE_NAME.format(country_id)

        self._country_id = country_id
        self._input_path = population_input_folder + POPULATION_FILE_NAME
        self._population_output_path = output_folder + pop_output_file_name

        print(country_id)
        print("Initialize parent class Grid...")
        Grid.__init__(self, country_id=country_id, output_folder=output_folder,
                      input_folder=grid_input_folder, overwrite=overwrite)

        if not os.path.exists(self._population_output_path):
            print("Parsing population...")
            self.parse_population()
            print("Saving population...")
            self.save_compressed_population()
        print("Loading population...")
        self.load_compressed_population()

        #print("Total population:", self.total_population())


    def population_array(self):

        return self._population.copy()


    def total_population(self):
        population = self._population
        total_population = population[population > 0].sum()

        return total_population


    def load_compressed_population(self):

        input_file = self._population_output_path

        population = []

        with open(input_file, "r") as infile:

            n_col = int(infile.readline()[:-1].split(" ")[-1])
            n_row = int(infile.readline()[:-1].split(" ")[-1])
            self._llcrnrlon = float(infile.readline()[:-1].split(" ")[-1])
            self._llcrnrlat = float(infile.readline()[:-1].split(" ")[-1])
            self._cellsize = float(infile.readline()[:-1].split(" ")[-1])

            for _ in range(2):
                infile.readline()

            population = np.zeros((n_row, n_col))

            for _ in range(n_row):
                indices = infile.readline()
                decompressed = _decompress(indices)
                population[_] = np.array(decompressed)
                print(_, end="\r")

        self._nlat = n_row
        self._nlon = n_col
        self._population = population

        print("Done..")


    def latitude_range(self):

        lats = self._llcrnrlat + np.arange(self._nlat) * self._cellsize

        return lats


    def longitude_range(self):

        lons = self._llcrnrlon + np.arange(self._nlon) * self._cellsize

        return lons


    def save_compressed_population(self):

        output_filepath = self._population_output_path
        population = self._population

        max_value = len(population)

        n_row, n_col = population.shape
        outstring = ""
        outstring += "ncols {0}\n".format(n_col)
        outstring += "nrows {0}\n".format(n_row)
        outstring += "llcrnrlon {0}\n".format(self._llcrnrlon)
        outstring += "llcrnrlat {0}\n".format(self._llcrnrlat)
        outstring += "cellsize {0}\n".format(self._cellsize)
        outstring += "NOTINCOUNTRY_value -2\nNODATA_value -1\n"

        print(outstring)
        for _, entry in enumerate(population):
            print(_, max_value, end="\r")
            outstring += _compress(entry)+"\n"

        with open(output_filepath, "w") as outfile:
            outfile.write(outstring)


    def parse_population(self, accuracy=3):

        print("Parsing population...")
        coords = self._country_coords
        input_path = self._input_path

        population = np.zeros((10800*2, 10800*4))

        valid_x = set()
        valid_y = set()

        for file_id, file_coords in coords.items():

            x_offset = 10800 * ((file_id-1) % 4)
            y_offset = 10800 * (file_id > 4)

            with open(input_path.format(file_id)) as infile:

                for _ in range(4):
                    infile.readline()

                cellsize = infile.readline()
                cellsize = float(cellsize[:-1].split(" ")[-1])

                infile.readline()

                all_y = list(file_coords.keys())
                min_index = np.min(all_y)
                max_index = np.max(all_y)

                for _ in range(min_index):
                    infile.readline()

                for i in range(max_index - min_index + 1):
                    print(file_id, i, len(population), end="\r")
                    row_id = min_index + i
                    if row_id not in all_y:
                        continue

                    col_id = file_coords[row_id]

                    line = infile.readline()
                    line = line.split(" ")
                    assert line[0] != ""
                    assert line[-1] == "\n"
                    assert len(line) == 10801

                    coords_x = [_x + x_offset for _x in col_id]
                    coords_y = [row_id + y_offset] * len(col_id)

                    valid_x.update(coords_x)
                    valid_y.update((row_id + y_offset,))

                    pop = [float(line[_x]) + 2 for _x in col_id]
                    population[(coords_y, coords_x)] = pop

                print()

        min_x = np.min(list(valid_x))
        max_x = np.max(list(valid_x))
        min_y = np.min(list(valid_y))
        max_y = np.max(list(valid_y))

        population = population[min_y:(max_y+1), min_x:(max_x+1)]
        population -= 2
        population[population < -1000] = -1

        max_value = len(population)

        # Do this on for-loop to be light on memory
        for i in range(max_value):
            print("Rounding:", i, max_value, end="\r")
            population[i] = np.round(population[i], accuracy)

        print(min_x, max_x, min_y, max_y)
        self._population = population
        self._llcrnrlon = (min_x * cellsize) % 360 - 180
        self._llcrnrlat = (180 - max_y * cellsize) % 180 - 90
        self._cellsize = cellsize


def main():
    Population(country_id=68)


if __name__ == "__main__":
    main()
