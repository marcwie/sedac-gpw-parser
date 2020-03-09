#!/usr/bin/env python3
"""
Generate an index that lists for each country the corresponding file ids.

The population data from the Socioeconomic Data and Applications Center (sedac)
is split into eight files.

This script goes through each file and finds all countries that are
included in them.

The script then generates an output file contaning space separated line for
each country with entries:
    COUNTRY_ID COMMA_SEPARATED_LIST_OF_FILE_IDS

For example if country 176 is present in file number 1,3 and 4 the line in the
output file reads:
    176 1,3,4
"""
import os

GRID_DATA = "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"\
        "gpw_v4_national_identifier_grid_rev11_30_sec_{0}.asc"

def main():
    """
    The main function.

    Goes trough each input file and finds all countries that are included in
    them. See module docstring for detailed explanation
    """
    if not os.path.exists("output"):
        os.mkdir("output")

    file_ids = {}

    for i in range(1, 9):

        i = str(i)
        print(i)

        current_ids = set()

        with open(GRID_DATA.format(i)) as infile:

            # Itereate over the header and print the content
            for _ in range(6):
                print(infile.readline()[:-1])

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
            if int(j) in file_ids.keys():
                file_ids[int(j)].append(i)
            else:
                file_ids[int(j)] = [i]


    with open("output/file_index.txt", "w") as outfile:
        outfile.write("#COUNTRY_ID FILE_IDS\n")
        for country_id, file_ids in file_ids.items():
            line = str(country_id) + " " + ",".join(file_ids) + "\n"
            outfile.write(line)


if __name__ == "__main__":
    main()
