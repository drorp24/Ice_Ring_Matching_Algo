from random import random, Random
from typing import List, Dict, Tuple

from experiment_space.analyzer.analyzer import Analyzer
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d
from visualization.basic.pltgantt_drawer import create_gantt_drawer
from visualization.operational import operational_drawer2d, operational_gantt_drawer
import matplotlib.pyplot as plt


def draw_matched_scenario(delivery_board, graph, supplier_category, map_image):
    draw_operational_graph_on_map(graph, map_image, should_block=False)
    draw_matches_on_map(delivery_board, map_image, should_block=False)
    draw_match_gantt(delivery_board, supplier_category, should_block=True)


def draw_multianalysis_graph(experiment_analysis_results: List[Dict], analyzers: List[Analyzer],
                             title: str, xlabel: str, ylabel: str, color: Tuple = (0, 0, 1, 0.5)):
    indexed_results = [(str(i), result) for i, result in enumerate(experiment_analysis_results)]
    xlabel = 'index' if xlabel is None else xlabel
    ylabel = sum([a.__name__ + ' ' for a in analyzers]) if ylabel is None else ylabel
    title = sum([a.__name__ + ' ' for a in analyzers]) + ' per Experiment' if title is None else title
    draw_labeled_analysis_graph(indexed_results, analyzers, title, xlabel, ylabel, color)


def draw_analysis_graph(experiment_analysis_results: List[Dict], analyzer: Analyzer,
                        title: str, xlabel: str, ylabel: str, color: Tuple = (0, 0, 1, 0.5)):
    indexed_results = [(str(i), result) for i, result in enumerate(experiment_analysis_results)]
    xlabel = 'index' if xlabel is None else xlabel
    ylabel = analyzer.__name__ if ylabel is None else ylabel
    title = analyzer.__name__ + ' per Experiment' if title is None else title
    draw_labeled_analysis_graph(indexed_results, [analyzer], title, xlabel, ylabel, color)


def draw_labeled_analysis_graph(experiment_analysis: List[Tuple[str, Dict]], analyzers: List[Analyzer],
                                title: str, xlabel: str, ylabel: str, color: Tuple = (0, 0, 1, 0.5), seed=42):
    fig, ax = plt.subplots(constrained_layout=True)
    for i, analyzer in enumerate(analyzers):
        color = (Random(seed + i).random(), Random(seed + i*100).random(), Random(seed + i*1000).random(), 0.5)
        x_experiment_label, y_analysis_output = _extract_x_y_from_labeled_experiment(analyzer, experiment_analysis)
        ax.plot(x_experiment_label, y_analysis_output, 'o', color=color, linestyle='solid', linewidth=2, markersize=10, markerfacecolor=color, label=analyzer.__name__)
    _add_wording_to_plot(ax, title, xlabel, ylabel)
    ax.grid('on')
    plt.legend()
    plt.show()


def draw_labeled_analysis_bar_chart(labeled_experiment_analysis: List[Tuple[str, Dict]], analyzer: Analyzer,
                                    title: str, xlabel: str, ylabel: str, color: Tuple = (0, 0, 1, 0.5)):
    fig, ax = plt.subplots(constrained_layout=True)
    x_experiment_label, y_analysis_output = _extract_x_y_from_labeled_experiment(analyzer, labeled_experiment_analysis)
    ax.bar(x_experiment_label, y_analysis_output, align='center', color=color)
    _add_wording_to_plot(ax, title, xlabel, ylabel)
    ax.grid('on')
    plt.show()


def draw_match_gantt(delivery_board, supplier_category, should_block):
    row_names = _get_row_names(delivery_board)
    board_gantt_drawer = create_gantt_drawer(zero_time=supplier_category.zero_time,
                                             hours_period=24,
                                             row_names=row_names,
                                             rows_title='Formation Type x Package Type Amounts')
    operational_gantt_drawer.add_delivery_board(board_gantt_drawer, delivery_board, draw_unmatched=True)
    board_gantt_drawer.draw(should_block)


def draw_matches_on_map(delivery_board, map_image, should_block=False):
    board_map_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
    operational_drawer2d.add_delivery_board(board_map_drawer, delivery_board, draw_unmatched=True)
    board_map_drawer.draw(should_block)


def draw_operational_graph_on_map(graph, map_image, should_block=False):
    dr_drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC, map_image)
    operational_drawer2d.add_operational_graph(dr_drawer, graph, draw_internal=True, draw_edges=True)
    dr_drawer.draw(should_block)


def _extract_x_y_from_labeled_experiment(analyzer: Analyzer,
                                         labeled_experiment_analysis_results: List[Tuple[str, Dict]]):
    x_experiment_label = [res[0] for res in labeled_experiment_analysis_results]
    y_analysis_output = [res[1][analyzer.__name__] for res in labeled_experiment_analysis_results]
    return x_experiment_label, y_analysis_output


def _add_wording_to_plot(ax, title, xlabel, ylabel):
    ax.set_title(title, fontdict={'weight': 'bold', 'size': 12})
    ax.set_xlabel(xlabel, fontdict={'style': 'italic', 'size': 10})
    ax.set_ylabel(ylabel, fontdict={'style': 'italic', 'size': 10})
    ax.figure.autofmt_xdate()


def _get_row_names(delivery_board):
    return ["Unmatched Out"] + \
           ["[" + str(delivery.drone_formation.drone_formation_type.name) + "] * " +
            str(delivery.drone_formation.drone_package_configuration.package_type_map)
            for delivery in delivery_board.drone_deliveries]
