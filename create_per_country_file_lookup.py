#!/usr/bin/env python3
import numpy as np
import os

GRID_DATA = "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"\
        "gpw_v4_national_identifier_grid_rev11_30_sec_{0}.asc"

def parse_files(country_id, file_ids):
    
    coords = {}
    
    for file_id in file_ids:

        with open(GRID_DATA.format(file_id)) as infile:
           
            file_coords = {}

            # Itereate over the header and print the content
            for _ in range(6):
                print(infile.readline()[:-1])

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

    return coords


def load_file_index():

    with open("output/file_index.txt", "r") as infile:
        infile.readline()
        file_index = {}
        for line in infile.readlines():
            country_id, file_list = line.split(" ")
            file_index[int(country_id)] = file_list[:-1].split(",")
    
    return file_index


def create_ranges(array):

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


def write_output_file(country_id, coords, outfile_name):

    header = "#file_id, line_number, column_numbers\n"
    
    with open(outfile_name, "w") as outfile:
        outfile.write(header)
        for file_id, file_coords in coords.items():
            for line_id, col_ids in file_coords.items():
                col_ranges = create_ranges(col_ids)
                line = "{0} {1} {2}\n".format(file_id, line_id, col_ranges)
                outfile.write(line)


def run(country_id, overwrite=False):

    outfile_name = "output/{0}_valid_indices.txt".format(country_id)
    if os.path.exists(outfile_name):
        print("Data for country {0} exists.".format(country_id), end=" ")
        if overwrite:
            print("Overwriting...")
        else:
            print("Skipping...")
            return 

    file_index = load_file_index()
    coords = parse_files(country_id, file_index[country_id])
    write_output_file(country_id, coords, outfile_name)
    print("Country {0} done!".format(country_id))
            

def main():

    file_index = load_file_index()
    for country_id in file_index.keys():
        print("Parsing files for country {0}...".format(country_id))
        run(country_id)


if __name__ == "__main__":
    main()
