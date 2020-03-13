"""
Plot statistics of a country's spatial population distribution.

Relies on parsing input data that has been preprocessed by the classes Grid and
Population.
"""

import os
from matplotlib import pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from population import Population

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
        ll_x = self._llcrnrlon
        ll_y = self._llcrnrlat
        cellsize = self._cellsize
        n_row, n_col = data.shape

        extent = (ll_x, ll_x + n_col * cellsize, ll_y, ll_y + n_row * cellsize)
        self._img_extent = extent


    def plot(self, title=""):

        img_extent = self._img_extent
        data = self._population

        ll_x, ur_x, ll_y, ur_y = img_extent

        # Set up the plot
        fig = plt.figure(figsize=(8*(ur_x - ll_x)/(ur_y - ll_y), 8))
        axs = plt.axes(projection=ccrs.PlateCarree())
        plt.subplots_adjust(right=0.85, left=0.05, bottom=0.05, top=0.95)

        # Draw map
        border = cfeature.NaturalEarthFeature(
            'cultural', 'admin_0_countries', '50m', edgecolor='black',
            facecolor="None")
        axs.add_feature(border, zorder=2, linewidth=0.5)
        axs.coastlines(resolution="50m", linewidth=1.5, zorder=3)

        cmap = cm.get_cmap("Purples")
        cmap.set_under('0.8')

        delta_x = (ur_x - ll_x) * 0.025
        delta_y = (ur_y - ll_y) * 0.025
        axs.set_extent(
            (ll_x - delta_x, ur_x + delta_x, ll_y - delta_y, ur_y + delta_y))

        if len(data[data > 0]) == 0:
            vmax = np.percentile(data[data > 0], 90)
        else:
            vmax = 0

        data_crs = ccrs.PlateCarree()
        colorscheme = axs.imshow(
            data, vmin=0, vmax=vmax, origin='upper', extent=img_extent,
            cmap=cmap, transform=data_crs)

        axpos = axs.get_position()
        pos_x = axpos.x0 + axpos.width + 0.025
        pos_y = axpos.y0 + axpos.height * 0.1
        cax_width = 0.025
        cax_height = axpos.height * 0.8
        cax = fig.add_axes([pos_x, pos_y, cax_width, cax_height])

        cbar = plt.colorbar(colorscheme, cax=cax, extend="max", shrink=0.85)
        cbar.set_label("Population per pixel", size=12)

        axs.set_title(title)
        plt.savefig(self._output_path)


def main():
    plot = Plot(country_id=276)
    plot.plot()

if __name__ == "__main__":
    main()
