GRID_FOLDER = "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"
GRID_LOOKUP = "gpw_v4_national_identifier_grid_rev11_lookup.txt"


def id_lookup(searchterm, lookup_file=GRID_FOLDER+GRID_LOOKUP):

    success = False

    with open(lookup_file, "r") as infile:
        infile.readline()

        for line in infile:
            line = line.split("\t")
            country_id = line[0]
            country_name = line[3]
            
            if searchterm.lower() in country_name.lower().replace(" ", ""):
                print(country_name, ":", country_id)
                success = True

    if not success:
        print("No country found for search term:", searchterm)
