from plot import Plot
import os

country_codes =  "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"\
        "gpw_v4_national_identifier_grid_rev11_lookup.txt"

with open(country_codes, "r") as infile:
    infile.readline()
    info = [(int(line.split("\t")[0]), line.split("\t")[3]) for line in infile]

for c_id, name in info:

    if c_id in [554, 643, 840]:
        print(c_id, "caused errors in the past. Skipping for now...")
        continue

    if os.path.exists("plots/{0}.png".format(c_id)):
        print(c_id, "already present.")
    else:
        print("Running for country:", c_id)
        p = Plot(c_id)
        p.plot(title=name)

