import os
import numpy as np
from .grid import Grid

POPULATION_FILE_NAME = "gpw_v4_population_count_rev11_2020_30_sec_{0}.asc"
POP_OUTPUT_FILE_NAME = "{0}_population.txt"


def _decompress(indices):
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


    def __init__(self, country_id, output_folder="output/",
                 population_input_folder="gpw-v4-population-count-rev11_2020_30_sec_asc/",
                 grid_input_folder="gpw-v4-national-identifier-grid-rev11_30_sec_asc/",
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
         
        lats = np.arange(self._llcrnrlat, self._llcrnrlat + self._nlat * self._cellsize, self._cellsize)
        
        return lats


    def longitude_range(self):
         
        lons = np.arange(self._llcrnrlon, self._llcrnrlon + self._nlon * self._cellsize, self._cellsize)
        
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
