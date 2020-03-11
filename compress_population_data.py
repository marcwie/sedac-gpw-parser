import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from grid import Grid

POPULATION_DATA = "gpw-v4-population-count-rev11_2020_30_sec_asc/"\
        "gpw_v4_population_count_rev11_2020_30_sec_{0}.asc"


def population(coords):
    
    print("Loading population...")
    population = np.zeros((10800*2, 10800*4)) 

    valid_x = set()
    valid_y = set()
   
    for file_id, file_coords in coords.items():

        x_offset = 10800 * ((file_id-1) % 4)
        y_offset = 10800 * (file_id > 4)
        
        with open(POPULATION_DATA.format(file_id)) as infile:

            for _ in range(6):
                infile.readline()

            all_y = list(file_coords.keys())
            min_index = np.min(all_y)
            max_index = np.max(all_y)
            
            for _ in range(min_index):
                infile.readline()
            
            for i in range(max_index - min_index + 1):
                print(i, len(population), end="\r")
                y = min_index + i
                if y not in all_y:
                    continue

                x = file_coords[y]

                line = infile.readline()
                line = line.split(" ")
                assert line[0] != ""
                assert line[-1] == "\n"
                assert len(line) == 10801

                coords_x = [_x + x_offset for _x in x]
                coords_y = [ y + y_offset ] * len(x)

                #coords_y = [ 10800 - y - 1 + y_offset ] * len(x)
                valid_x.update(coords_x)
                valid_y.update((y + y_offset,))

                pop = [float(line[_x]) + 2 for _x in x]
                population[(coords_y, coords_x)] = pop
            #data[i] = np.array(line.split(" ")).astype(float)
   
    min_x = np.min(list(valid_x))
    max_x = np.max(list(valid_x))
    min_y = np.min(list(valid_y))
    max_y = np.max(list(valid_y))
    print(min_x, max_x, min_y, max_y) 
    population = population[min_y:(max_y+1), min_x:(max_x+1)]
    population -= 2
    population[population < -1000] = -1

    print(population.shape, population.min())
    population = np.round(population, 3)

    return population


def plot_grid(coords):
    
    print("Loading population...")
    population = np.zeros((10800*2, 10800*4)) 

    valid_x = set()
    valid_y = set()
   
    for file_id, file_coords in coords.items():

        x_offset = 10800 * ((file_id-1) % 4)
        y_offset = 10800 * (file_id > 4)
        
        all_y = list(file_coords.keys())
        min_index = np.min(all_y)
        max_index = np.max(all_y)
            
        for i in range(max_index - min_index + 1):
            print(i, len(population), end="\r")
            y = min_index + i
            if y not in all_y:
                continue

            x = file_coords[y]
            coords_x = [_x + x_offset for _x in x]
            coords_y = [ y + y_offset ] * len(x)

            valid_x.update(coords_x)
            valid_y.update((y + y_offset,))

            population[(coords_y, coords_x)] = 1
            #data[i] = np.array(line.split(" ")).astype(float)
   
    min_x = np.min(list(valid_x))
    max_x = np.max(list(valid_x))
    min_y = np.min(list(valid_y))
    max_y = np.max(list(valid_y))
    print(min_x, max_x, min_y, max_y) 
    population = population[min_y:(max_y+1), min_x:(max_x+1)]

    print(population.shape)

    return population


def plot(population, country_name, suffix=""):
    if not os.path.exists("plots"):
        os.mkdir("plots")

    f = plt.figure()
    cmap = cm.get_cmap("Greens")
    cmap.set_under('0.5')
    
    plt.imshow(population, vmin=-1, vmax=np.nanpercentile(population, 95), cmap=cmap, origin='upper')

    plt.savefig("plots/{0}{1}.png".format(country_name, suffix))
    plt.close()



def compress(array):

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


def write(population, country_name):
    
    with open("output/{0}_population.txt", "w") as outfile:

        for pop in population:
            
            outfile.write(compress(pop)+"\n")


def load(country_name):

    population = []
    
    with open("output/{0}_population.txt", "r") as infile:

        for indices in infile:

            decompressed = []
            for entry in indices.split(" "):
                if "x" in entry:
                    counter, value = entry.split("x")
                else: 
                    counter = 1
                    value = entry
                decompressed.extend(int(counter) * [float(value)])
    
            population.append(decompressed)

    population = np.array(population)
    print(population.shape)
    return population

def run():
    country_id = 124 # Canada
    country_id = 276 # Germany
    country_id = 208 # Denmark
    country_id = 724 # Spain

    print("Initialize grid...")
    country_grid = Grid(country_id)
    coords = country_grid._country_coords

    print("Parse population...")
    pop = population(coords)
    plot(pop, country_id)

    print("Writing file...")
    write(pop, country_id)

    print("Load population back...")
    pop = load(country_id)
    plot(pop, country_id, suffix="_load")

    print("Total population:", pop[pop>0].sum())


def main():

    run()


if __name__ == "__main__":
    main()
