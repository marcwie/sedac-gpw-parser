from population import Population
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import cm
import numpy as np
import os
from mpl_toolkits.axes_grid1 import make_axes_locatable


class Plot(Population):

    def __init__(self, country_id, plot_folder="./plots/"):
        
        if not os.path.exists(plot_folder):
            os.mkdir(plot_folder)

        Population.__init__(self, country_id=country_id)

        self._country_id = country_id
        self.plot_folder = plot_folder
        
        self._output_path = plot_folder + str(country_id) + ".png"

        self._compute_image_extent()
        
    def _compute_image_extent(self):

        data = self._population
        x0 = self._llcrnrlon
        y0 = self._llcrnrlat
        cellsize = self._cellsize
        n_row, n_col = data.shape

        img_extent = (x0, x0+n_col*cellsize, y0, y0+n_row*cellsize)

        self._img_extent = img_extent


    def plot(self, title=""):

        img_extent =  self._img_extent
        data = self._population

        x0, x1, y0, y1 = img_extent
        print((x1-x0)/(y1-y0)) 
        f = plt.figure(figsize=(8*(x1 - x0)/(y1 - y0), 8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        plt.subplots_adjust(right=0.85, left=0.05, bottom=0.05, top=0.95)

        data_crs = data_crs = ccrs.PlateCarree()
        #ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
        #                                     edgecolor='face',
        #                                     facecolor=cfeature.COLORS['water'])
        border = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries',
                                              '50m', edgecolor='black',
                                              facecolor="None")

        #ax.add_feature(ocean, zorder=2)
        ax.add_feature(border, zorder=2, linewidth=0.5)
        ax.coastlines(resolution="50m", linewidth=1.5, zorder=3)

        cmap = cm.get_cmap("Purples")
        cmap.set_under('0.8')

        delta_x = (x1 - x0) * 0.025
        delta_y = (y1 - y0) * 0.025
        ax.set_extent((x0 - delta_x, x1 + delta_x, y0 - delta_y, y1 + delta_y))

        if len(data[data>0]):
            vmax = np.percentile(data[data > 0], 90)
        else:
            vmax = 0

        cs = ax.imshow(data, vmin=0, vmax=vmax, origin='upper',
                       extent=img_extent, cmap=cmap)

        axpos = ax.get_position()
        pos_x = axpos.x0+axpos.width + 0.025
        pos_y = axpos.y0 + axpos.height * 0.1
        cax_width = 0.025
        cax_height = axpos.height * 0.8
        #create new axes where the colorbar should go.
        #it should be next to the original axes and have the same height!
        cax = f.add_axes([pos_x,pos_y,cax_width,cax_height])

        cbar = plt.colorbar(cs, cax=cax, extend="max", shrink=0.85)#, pad=0.025)
        cbar.set_label("Population per pixel", size=12)

        ax.set_title(title)
        plt.savefig(self._output_path)


if __name__ == "__main__":
    p = Plot(country_id=116)
    p.plot()
