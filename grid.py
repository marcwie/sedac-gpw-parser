import os
import numpy as np

GRID_FILENAME = "gpw_v4_national_identifier_grid_rev11_30_sec_{0}.asc"
COUNTRY_COORDS_FILENAME = "{0}_valid_indices.txt"
FILE_INDEX_NAME = "file_index.txt"

class Grid():
    
    def __init__(self, country_id, output_folder="output/",
                 input_folder="gpw-v4-national-identifier-grid-rev11_30_sec_asc/",
                 overwrite=False):

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
       
        country_id = self._country_id
        file_ids = self._file_ids
        grid_path = self._grid_path

        coords = {}
        
        for file_id in file_ids:
    
            with open(grid_path.format(file_id)) as infile:
               
                file_coords = {}

                # Skip the header
                self._skip_header(infile)
    
                # Iterate over each line containing data
                for y in range(10800):
                    
                    print(y, end="\r")
                    line = infile.readline()
                    if " {0} ".format(country_id) in line:
                        line = line.split(" ")
                        assert line[0] != ""
                        assert line[-1] == "\n"
                        assert len(line) == 10801
                        x = [_x for _x in range(10800) if line[_x] == str(country_id)]
                        file_coords[y] = x
    
                # Check that all lines have really been read
                assert infile.readline() == ""
    
                coords[file_id] = file_coords
    
        self._country_coords = coords


    def _compress(self, array):
    
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
    
    
    def save_country_coords(self):
   
        outfile_name = self._country_coords_path
        coords = self._country_coords

        header = "#file_id, line_number, column_numbers\n"

        with open(outfile_name, "w") as outfile:
            outfile.write(header)
            for file_id, file_coords in coords.items():
                for line_id, col_ids in file_coords.items():
                    col_ranges = self._compress(col_ids)
                    line = "{0} {1} {2}\n".format(file_id, line_id, col_ranges)
                    outfile.write(line)


    def _decompress(self, ranges):

        resolved_range = []

        for one_range in ranges:
            lower_bound, upper_bound = one_range.split(",")
            for _ in range(int(lower_bound), int(upper_bound)):
                resolved_range.append(_)

        return resolved_range


    def load_country_coords(self):
       
        file_ids = self._file_ids
        file_name = self._country_coords_path

        coords = {file_id: {} for file_id in file_ids}

        with open(file_name, "r") as infile:
            infile.readline()

            for line in infile:
                line = line[:-1].split(" ")
                file_id = int(line[0])
                row_id = int(line[1])
                col_ids = self._decompress(line[2:])
                
                coords[file_id][row_id] = col_ids
        
        self._country_coords = coords
       
    
    def _skip_header(self, infile):
        # Itereate over the header and print the content
        for _ in range(6):
            print(infile.readline()[:-1])


    def generate_file_index(self):
        print("Generating file index...")

        grid_path = self._grid_path

        file_index = {}

        for i in range(1, 9):
            current_ids = set()

            with open(grid_path.format(i)) as infile:

                self._skip_header(infile)

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
        
        file_index = self._file_index
        file_index_path = self._file_index_path

        with open(file_index_path, "w") as outfile:
            outfile.write("#COUNTRY_ID FILE_IDS\n")
            for country_id, file_ids in file_index.items():
                file_ids = [str(_f) for _f in file_ids]
                line = str(country_id) + " " + ",".join(file_ids) + "\n"
                outfile.write(line)


    def load_file_index(self):
        
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
