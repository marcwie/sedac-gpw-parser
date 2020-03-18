"""
Framework for working with the grid provided with the SEDAC GPW data set.

For a given country this file provides helpers to find the coordinates of that
country across the 8 different input files.

Particularly, the provided class Grid contains a formalism to store the grid
for each country in a space-efficient on the disk. For this a custom file
format is used that contains all valid grid points of a country.

An example of an output file could look like this:

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
- The second entry is the line number that contains relevant data
  (starting from 0 after the file header)
- All following entries are pairs of lower (inclusive) and upper bounds
  (exclusive) for ranges of column numbers. For example `1,3 6,7, 8,10`
  would correspond to column numbers `1,2,6,8,9`.

The data can be parsed from the origial source files are read from disk if it
was previously already processed using the Grid class.
"""
import os
import numpy as np

GRID_FILENAME = "gpw_v4_national_identifier_grid_rev11_30_sec_{0}.asc"
COUNTRY_COORDS_FILENAME = "{0}_valid_indices.txt"
FILE_INDEX_NAME = "file_index.txt"

def _compress(array):
    """
    Compress a one-dimensional list with sequential entries.

    If a range of consecutive numbers occurs within a list only the first and
    last entry of that range or stored. Using the function _decompress() this
    special format can be converted into the original list again.

    See the examples below for what the script does.

    :param array: The list that one wishes to compress.
    :type array: 1d numpy array or list

    :return: A representation of the compressed list or array.
    :rtype: str

    Examples:
    >>> _compress([0,1,3,4,5,8])
    '0,2 3,6 8,9'

    >>> _compress([0,3,4,5,8,9,13,14,15])
    '0,1 3,6 8,10 13,16'
    """
    mask = np.diff(array) != 1
    upper_bounds = np.array(array[:-1])[mask]
    lower_bounds = np.array(array[1:])[mask]
    lower_bounds = np.append(np.min(array), lower_bounds)
    upper_bounds = np.append(upper_bounds, np.max(array)) + 1

    lower_bounds = lower_bounds.astype(int)
    upper_bounds = upper_bounds.astype(int)

    assert len(lower_bounds) == len(upper_bounds)

    outstring = ""
    for lower_bound, upper_bound in zip(lower_bounds, upper_bounds):
        outstring += str(lower_bound) + "," + str(upper_bound) + " "

    outstring = outstring[:-1]

    return outstring


def _decompress(ranges):
    """
    Decompresses a list with sequential entries that is stored as a string
    created from _compress().

    See the help of _compress() for more information. Also see below for
    examples on the format of the input.

    :param ranges: Specially formatted strings containing the ranges in the
                   desired list.
    :type range: list of str

    Examples:
    >>> _decompress(['0,2', '3,6', '8,9'])
    [0, 1, 3, 4, 5, 8]

    >>> _decompress(['0,1', '3,6', '8,10', '13,16'])
    [0, 3, 4, 5, 8, 9, 13, 14, 15]
    """
    resolved_range = []

    for one_range in ranges:
        lower_bound, upper_bound = one_range.split(",")
        for _ in range(int(lower_bound), int(upper_bound)):
            resolved_range.append(_)

    return resolved_range


def _skip_header(infile):
    """
    Skip the first 6 lines in a file.

    Useful to skip the header in the sedac-gpw input files as they usually
    contain the following entries (or similar):

    ncols         10800
    nrows         10800
    xllcorner     -180
    yllcorner     0
    cellsize      0.0083333333333333
    NODATA_value  -9999

    :param infile: The file-object that was opened using f = open(...)
    :type infle: io.TextIOWrapper
    """
    # Itereate over the header and print the content
    for _ in range(6):
        print(infile.readline()[:-1])


class Grid():
    """
    Methods for reading the gpw population data grid and storing a condensed
    version of a per-country grid to disk for later use.
    """
    def __init__(
            self, country_id, output_folder="output/",
            input_folder="gpw-v4-national-identifier-grid-rev11_30_sec_asc/",
            overwrite=False):
        """Initialize an instance of Grid.

        :param country_id: The numerical ID of a country in the population
                           dataset. A list of valid IDs is found in the
                           grid-data's lookup table.
        :type country_id: int

        :param output_folder: The relative path to the desired output folder.
        :type output_folder: str

        :param input_folder: The relative path to the input data containing the
                             eight grid files.
        :type input_folder: str

        :param overwrite: If True, existing data will be written over.
        :type overwrite: bool
        """

        assert not overwrite, "Not implemented yet!"

        country_coords_filename = COUNTRY_COORDS_FILENAME.format(country_id)

        self._grid_path = input_folder + GRID_FILENAME
        self._file_index_path = output_folder + FILE_INDEX_NAME
        self._country_coords_path = output_folder + country_coords_filename
        self._country_id = country_id

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        # Get the correct file ids for the given country
        if not os.path.exists(self._file_index_path):
            self.generate_file_index()
            self.save_file_index()
        self.load_file_index()

        # Get the coordinates in each file that represent the given country
        if not os.path.exists(self._country_coords_path):
            self.parse_country_coords()
            self.save_country_coords()
        self.load_country_coords()


    def parse_country_coords(self):
        """
        Obtain all coordinates in the grid input files that represent the
        considered country.
        """
        country_id = self._country_id
        file_ids = self._file_ids
        grid_path = self._grid_path

        coords = {}

        for file_id in file_ids:

            with open(grid_path.format(file_id)) as infile:

                file_coords = {}

                # Skip the header
                _skip_header(infile)

                # Iterate over each line containing data
                for row_id in range(10800):

                    print(row_id, end="\r")
                    line = infile.readline()
                    if " {0} ".format(country_id) in line:
                        line = line.split(" ")
                        assert line[0] != ""
                        assert line[-1] == "\n"
                        assert len(line) == 10801
                        col_ids = [_x for _x in range(10800) if line[_x] == str(country_id)]
                        file_coords[row_id] = col_ids

                # Check that all lines have really been read
                assert infile.readline() == ""

                coords[file_id] = file_coords

        self._country_coords = coords


    def save_country_coords(self):
        """
        Dump the coordinates to a file for later use.

        Uses a custom file format to save space on the disk and to allow for
        fast processing.

        An example of an output file could look like this:

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
        - The second entry is the line number that contains relevant data
          (starting from 0 after the file header)
        - All following entries are pairs of lower (inclusive) and upper bounds
          (exclusive) for ranges of column numbers. For example `1,3 6,7, 8,10`
          would correspond to column numbers `1,2,6,8,9`.
        """
        outfile_name = self._country_coords_path
        coords = self._country_coords

        header = "#file_id, line_number, column_numbers\n"

        with open(outfile_name, "w") as outfile:
            outfile.write(header)
            for file_id, file_coords in coords.items():
                for line_id, col_ids in file_coords.items():
                    col_ranges = _compress(col_ids)
                    line = "{0} {1} {2}\n".format(file_id, line_id, col_ranges)
                    outfile.write(line)


    def load_country_coords(self):
        """
        Load previously dumpled coordinates for the country from the disk.

        Requires files formatted as shown in the documentation of
        Grid.save_country_coords(). Usually this function can only be called
        after Grid.save_country_coords() has been called once for the country
        under consideration.
        """
        file_ids = self._file_ids
        file_name = self._country_coords_path

        coords = {file_id: {} for file_id in file_ids}

        with open(file_name, "r") as infile:
            infile.readline()

            for line in infile:
                line = line[:-1].split(" ")
                file_id = int(line[0])
                row_id = int(line[1])
                col_ids = _decompress(line[2:])

                coords[file_id][row_id] = col_ids

        self._country_coords = coords


    def generate_file_index(self):
        """
        Generate an index that contains for each country in the population data
        set a mapping between the country ids and the input files that contain
        the country.

        This file is dumped to disk and used later to only load those files for
        a given country that contain relevant data.
        """
        print("Generating file index...")

        grid_path = self._grid_path

        file_index = {}

        for i in range(1, 9):
            current_ids = set()

            with open(grid_path.format(i)) as infile:

                _skip_header(infile)

                # Iterate over each line containing data
                for j in range(10800):
                    line = infile.readline()[:-1]
                    while line[-1] == " ":
                        line = line[:-1]
                    line = set(line.split(" "))
                    current_ids.update(line)

                # Check that all lines have really been read
                assert infile.readline() == ""

            current_ids.discard("-32768")

            for j in current_ids:
                if int(j) in file_index.keys():
                    file_index[int(j)].append(i)
                else:
                    file_index[int(j)] = [i]

        self._file_index = file_index


    def save_file_index(self):
        """
        Dump the file index generated with Grid.generate_file_index() to disk.

        The file will have the following structure:

        #COUNTRY_ID FILE_IDS
        222 1,2
        643 1,3,4
        320 1,2
        484 1,2
        296 1,4,5,8

        The first entry in each row is the country id, the second
        (comma-separated) entry contains the indices of those input files that
        contain relevant data on the country.

        For example if country 176 is present in file number 1,3 and 4 the line
        in the output file reads:
        176 1,3,4
        """
        file_index = self._file_index
        file_index_path = self._file_index_path

        with open(file_index_path, "w") as outfile:
            outfile.write("#COUNTRY_ID FILE_IDS\n")
            for country_id, file_ids in file_index.items():
                file_ids = [str(_f) for _f in file_ids]
                line = str(country_id) + " " + ",".join(file_ids) + "\n"
                outfile.write(line)


    def load_file_index(self):
        """
        Load a previously dumped file index.

        This function is usually oncly called after the file index was
        generated with Grid.generate_file_index() and dumped to disk using
        Grid.save_file_index().
        """
        file_index_path = self._file_index_path
        country_id = self._country_id

        with open(file_index_path, "r") as infile:
            infile.readline() # Skipping the header
            file_index = {}
            for line in infile.readlines():
                country, file_list = line.split(" ")
                file_list = file_list[:-1].split(",")
                file_list = [int(_f) for _f in file_list]
                file_index[int(country)] = file_list

        self._file_index = file_index
        self._file_ids = file_index[country_id]
