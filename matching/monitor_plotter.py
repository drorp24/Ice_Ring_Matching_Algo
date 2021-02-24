import matplotlib.pyplot as plt
from matplotlib import figure

from matching.matcher_input import MatcherInput
from matching.monitor import MonitorData, current_milli_time

from os import path
import os

def create_monitor_figure (monitor, matcher_input: MatcherInput):
    fig_num = len(plt.get_fignums())
    plt.figure(fig_num, figsize=(15, 10))

    plot_data_list = [MonitorData.objective.name,
                      MonitorData.total_priority.name,
                      MonitorData.total_unmatched_delivery_requests.name,
                      MonitorData.unmatched_delivery_requests_total_priority.name]
    fig, ax = plt.subplots(2, 2, num=fig_num, sharex=True)

    fig_title = f'first solution strategy: {matcher_input.config.solver.first_solution_strategy}, local search strategy: {matcher_input.config.solver.local_search_strategy}, unmatched penalty: {matcher_input.config.unmatched_penalty}'
    fig.suptitle(fig_title)
    short_title = f'{matcher_input.config.solver.first_solution_strategy}-{matcher_input.config.solver.local_search_strategy}-{matcher_input.config.unmatched_penalty}'
    fig.canvas.set_window_title(short_title)

    x = monitor.data[MonitorData.iterations.name].values

    for plot_index, data_name in enumerate(plot_data_list):
        y = monitor.data[data_name].values
        plot(ax[int(plot_index / 2)][plot_index % 2], x, y, x_label=MonitorData.iterations.name, y_label=data_name)

    if matcher_input.config.monitor.save_data:
        _save_monitor_figure(fig, short_title, matcher_input.config.monitor.output_directory)

    if not matcher_input.config.monitor.plot_data:
        plt.close(fig)


def _save_monitor_figure(fig: figure.Figure, title: str, output_directory: str):
    if not path.exists(output_directory):
        os.makedirs(output_directory)

    file_name = f"Monitor_{title.replace(' ', '_')}{str(current_milli_time())}.png"
    fig.savefig(path.join(output_directory, file_name))


def plot(ax, x, y, x_label, y_label):
    ax.plot(x, y, linewidth=5)
    ax.set_title(y_label)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis='both', labelsize=14)
    ax.ticklabel_format(useOffset=True)
    plt.subplots_adjust(wspace=0.6, hspace=0.5, left=0.1, bottom=0.2, right=0.96, top=0.9)



