"""
Parse, compress, store and plot the population for every country.

This script starts the entire analysis pipeline and creates two main outputs
for each valid country:

    1. Two compressed files containing information (i) the grid representing
    the relevant data points for this country and (ii) the corresponding
    population count per grid cell.

    2. A plot of the spatial population distribution. The main purpose of this
    plot is to assist with visual quality control of the data and the analysis
    pipeline.
"""
import os
from .plot import Plot

COUNTRY_CODES = "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"\
        "gpw_v4_national_identifier_grid_rev11_lookup.txt"

def main():
    """
    Load the list of valid country codes and create output for each country.

    Two output files and one plot are created for each country.
    """
    with open(COUNTRY_CODES, "r") as infile:
        infile.readline()
        info = [(int(_l.split("\t")[0]), _l.split("\t")[3]) for _l in infile]

    for c_id, name in info:

        if c_id in [554, 643, 840]:
            # 554, 643, 840 the three countries that span the -180/180 degree
            # latitude line and hence cause an array of population data that is
            # too large to be plotted on a map.
            # These countries are:
            # - New Zealand (554)
            # - Russia (643)
            # - USA (840)
            print(c_id, "caused errors in the past. Skipping for now...")
            continue

        if os.path.exists("plots/{0}.png".format(c_id)):
            print(c_id, "already present.")
        else:
            print("Running for country:", c_id)
            plot = Plot(c_id)
            plot.plot(title=name)

if __name__ == "__main__":
    main()
