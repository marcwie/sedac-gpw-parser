import os

GRID_FOLDER = "gpw-v4-national-identifier-grid-rev11_30_sec_asc/"
GRID_LOOKUP = "gpw_v4_national_identifier_grid_rev11_lookup.txt"
DATA_FOLDER = os.path.expanduser("~") + "/.sedac_gpw_parser/"

def id_lookup(searchterm, lookup_file=DATA_FOLDER+GRID_FOLDER+GRID_LOOKUP,
              verbose=True):

    success = False

    names_ids = []
    
    searchterm = searchterm.lower().replace(" ", "")

    with open(lookup_file, "r") as infile:
        infile.readline()

        for line in infile:
            line = line.split("\t")
            country_id = line[0]
            country_name = line[3]
            
            if searchterm.lower() in country_name.lower().replace(" ", ""):
                if verbose:
                    print(country_name, ":", country_id)
                success = True
                names_ids.append((country_name, int(country_id)))

    if not success:
        if verbose:
            print("No country found for search term:", searchterm)

    return names_ids
