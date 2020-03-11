import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
from grid import Grid

POPULATION_FILE_NAME = "gpw_v4_population_count_rev11_2020_30_sec_{0}.asc"
POP_OUTPUT_FILE_NAME = "{0}_population.txt"

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
        
        print("Total population:", self.total_population())
             
    
    def total_population(self):
        population = self._population
        total_population = population[population>0].sum()

        return total_population


    def decompress(self, indices):
        decompressed = []
        for entry in indices.split(" "):
            if "x" in entry:
                counter, value = entry.split("x")
            else: 
                counter = 1
                value = entry
            decompressed.extend(int(counter) * [float(value)])
        return decompressed 


    def load_compressed_population(self):

        input_file = self._population_output_path 

        population = []
        
        with open(input_file, "r") as infile:
            
            counter = 0
            while True:
                indices = infile.readline()
                if indices == "":
                    break
                decompressed = self.decompress(indices) 
                population.append(np.array(decompressed))
                print(counter, end="\r")
                counter += 1
                
        pop_array = np.zeros((len(population), len(population[0])))
        max_value = len(population)
        for i in range(max_value):
            pop_array[i] = population[i]
       
        self._population = pop_array
        print("Done..")


    def _compress(self, array):
    
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


    def save_compressed_population(self):
    
        output_filepath = self._population_output_path 
        population = self._population
        
        max_value = len(population)

        outstring = ""
        for _, entry in enumerate(population):
            print(_, max_value, end="\r")
            outstring += self._compress(entry)+"\n"

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
    
                for _ in range(6):
                    infile.readline()
    
                all_y = list(file_coords.keys())
                min_index = np.min(all_y)
                max_index = np.max(all_y)
                
                for _ in range(min_index):
                    infile.readline()
                
                for i in range(max_index - min_index + 1):
                    print(file_id, i, len(population), end="\r")
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

                print()
                #data[i] = np.array(line.split(" ")).astype(float)
       
        min_x = np.min(list(valid_x))
        max_x = np.max(list(valid_x))
        min_y = np.min(list(valid_y))
        max_y = np.max(list(valid_y))

        population = population[min_y:(max_y+1), min_x:(max_x+1)]
        population -= 2
        population[population < -1000] = -1
     
        max_value = len(population)
        for i in range(len(population)):
            print("Rounding:", i, max_value, end="\r")
            population[i] = np.round(population[i], accuracy)

        self._population = population


#def plot_grid(coords):
#    
#    print("Loading population...")
#    population = np.zeros((10800*2, 10800*4)) 
#
#    valid_x = set()
#    valid_y = set()
#   
#    for file_id, file_coords in coords.items():
#
#        x_offset = 10800 * ((file_id-1) % 4)
#        y_offset = 10800 * (file_id > 4)
#        
#        all_y = list(file_coords.keys())
#        min_index = np.min(all_y)
#        max_index = np.max(all_y)
#            
#        for i in range(max_index - min_index + 1):
#            print(i, len(population), end="\r")
#            y = min_index + i
#            if y not in all_y:
#                continue
#
#            x = file_coords[y]
#            coords_x = [_x + x_offset for _x in x]
#            coords_y = [ y + y_offset ] * len(x)
#
#            valid_x.update(coords_x)
#            valid_y.update((y + y_offset,))
#
#            population[(coords_y, coords_x)] = 1
#            #data[i] = np.array(line.split(" ")).astype(float)
#   
#    min_x = np.min(list(valid_x))
#    max_x = np.max(list(valid_x))
#    min_y = np.min(list(valid_y))
#    max_y = np.max(list(valid_y))
#    print(min_x, max_x, min_y, max_y) 
#    population = population[min_y:(max_y+1), min_x:(max_x+1)]
#
#    print(population.shape)
#
#    return population


#def plot(population, country_name, suffix=""):
#    if not os.path.exists("plots"):
#        os.mkdir("plots")
#
#    f = plt.figure()
#    cmap = cm.get_cmap("Greens")
#    cmap.set_under('0.5')
#    
#    plt.imshow(population, vmin=-1, vmax=np.nanpercentile(population, 95), cmap=cmap, origin='upper')
#
#    plt.savefig("plots/{0}{1}.png".format(country_name, suffix))
#    plt.close()

if __name__ == "__main__":
    pop = Population(country_id=276)
