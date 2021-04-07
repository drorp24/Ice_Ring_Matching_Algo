import math
import os
import numpy as np
from os import path
from typing import List
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import axes


class LineChartDrawer():

    def __init__(self, data: pd.DataFrame, x_name: str, y_names: List[str], title: str):
        fig_num = len(plt.get_fignums())
        plt.figure(fig_num, figsize=(15, 10))
        self._num_of_plots = len(y_names)

        x = data[x_name].values

        if self._num_of_plots > 1:
            num_of_columns = math.ceil(math.sqrt(self._num_of_plots))
            num_of_rows = math.ceil(self._num_of_plots / num_of_columns)
            self._fig, self._ax = plt.subplots(num_of_rows, num_of_columns, num=fig_num, sharex=True)
            for plot_index, data_name in enumerate(y_names):
                y = data[data_name].values
                if num_of_rows > 1:
                    self._plot(self._ax[int(plot_index / num_of_columns)][plot_index % num_of_columns], x, y,
                               x_label=x_name, y_label=data_name)
                else:
                    self._plot(self._ax[plot_index], x, y, x_label=x_name, y_label=data_name)
        else:
            self._fig, self._ax = plt.subplots(num=fig_num)
            data_name = y_names[0]
            y = data[data_name].values
            self._plot(self._ax, x, y, x_label=x_name, y_label=data_name)

        self._fig.suptitle(title)

    def draw(self, block=True) -> None:
        self._fig.show()
        # plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
        plt.show(block=block)

    def close_plot(self) -> None:
            plt.close(self._fig)

    def save_plot_to_png(self, output_directory: str, file_name: str) -> None:
        if not path.exists(output_directory):
            os.makedirs(output_directory)
        plt.savefig(path.join(output_directory, f'{file_name}.png'))

    @staticmethod
    def _plot(ax: axes.Axes, x:np.array, y:np.array, x_label: str, y_label: str):
        ax.plot(x, y, linewidth=5)
        ax.set_title(y_label)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.tick_params(axis='both', labelsize=14)
        ax.ticklabel_format(useOffset=True)
        plt.subplots_adjust(wspace=0.6, hspace=0.5, left=0.1, bottom=0.2, right=0.96, top=0.9)

