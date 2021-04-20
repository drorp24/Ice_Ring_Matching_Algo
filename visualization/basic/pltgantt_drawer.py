from datetime import timedelta
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, NullFormatter, FixedFormatter

from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension, TimeDeltaExtension, \
    MIN_IN_HOUR
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer

MARK_WIDTH_RATIO = 0.1
YLIMIT = 100
BAR_ALPHA = 0.6
BACKGROUND_ALPHA = 0.1


def create_gantt_drawer(zero_time: DateTimeExtension, hours_period: int, row_names: [str],
                        rows_title: str, alternating_row_color: bool = True) -> GanttDrawer:
    return PltGanttDrawer(zero_time, hours_period, row_names, rows_title, alternating_row_color)


class PltGanttDrawer(GanttDrawer):
    def __init__(self, zero_time: DateTimeExtension, hours_period: int, row_names: [str], rows_title: str,
                 alternating_row_color: bool = True):
        self._zero_time = zero_time
        self._hours_period = hours_period
        self._fig, self._ax = plt.subplots()
        self._row_names = row_names
        self._rows_title = rows_title
        self._row_y_factor = YLIMIT / len(row_names)

        self._set_plot_limits()
        self._set_xtick_locations_and_labels()
        self._set_ytick_locations_and_labels()
        if alternating_row_color:
            self._set_alternating_row_color()
        self._ax.set_xlabel('Hours since ' + self._zero_time.str_format_time())
        self._ax.set_ylabel(rows_title, labelpad=10)
        self._ax.grid(b=True)

    def add_bar(self, row: int, time_window: TimeWindowExtension, name: str, time_mark: DateTimeExtension = None,
                side_text: str = None, color: Color = Color.Blue, inner_row: int = 0, max_inner_rows: int = 1) -> None:
        since, until = time_window.get_relative_time_in_min(self._zero_time)
        bar_height = self._row_y_factor * 1 / max_inner_rows
        y = self._calc_y(row, inner_row, bar_height)
        if color is not Color.White:
            self._ax.barh(y=y, width=until - since, height=bar_height, left=since,
                          color=color.get_rgb_with_alpha(BAR_ALPHA), label=name,
                          edgecolor=Color.Black.get_rgb(), linewidth=1)
            if time_mark:
                relative_time_in_min = time_mark.get_time_delta(self._zero_time).in_minutes()
                mark_width = MARK_WIDTH_RATIO * self._hours_period
                self._ax.barh(y=y, width=mark_width, height=bar_height, left=relative_time_in_min - mark_width / 2,
                              color=color.Black.get_rgb())
            if side_text:
                self._ax.text(x=until + MARK_WIDTH_RATIO * self._hours_period, y=y - bar_height / 2, s=side_text,
                              color=Color.Black.get_rgb(), fontsize=9)
        else:
            if time_mark:
                relative_time_in_min = time_mark.get_time_delta(self._zero_time).in_minutes()
                mark_width = MARK_WIDTH_RATIO * self._hours_period
                self._ax.barh(y=y, width=mark_width, height=bar_height, left=relative_time_in_min - mark_width / 2,
                              color=color.Black.get_rgb())
                if side_text:
                    self._ax.text(x=relative_time_in_min + mark_width, y=y - bar_height / 2, s=side_text,
                                  color=Color.Black.get_rgb(), fontsize=9)

    def add_row_area(self, row: int, time_window: TimeWindowExtension,
                     facecolor: Color = Color.Red, face_alpha: float = 0,
                     edgecolor: Color = Color.Red) -> None:
        since, until = time_window.get_relative_time_in_min(self._zero_time)
        y = (row - 1) * self._row_y_factor + self._row_y_factor / 2
        self._ax.barh(y=y, width=until - since, height=self._row_y_factor, left=since,
                      facecolor=facecolor.get_rgb_with_alpha(face_alpha),
                      edgecolor=edgecolor.get_rgb(),
                      linewidth=2)

    def add_legend(self, new_labels: [str] = None, new_label_colors: [Color] = None, alpha: float = None,
                   fontsize: int = 10, title: str = None) -> None:
        if new_labels is not None:
            self._add_legend_with_new_labels(new_labels, new_label_colors, alpha, fontsize, title)
        else:
            plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left", ncol=3)

    def get_num_rows(self):
        return len(self._row_names)

    def get_zero_time(self):
        return self._zero_time

    def get_end_time(self):
        return self._zero_time.add_time_delta(TimeDeltaExtension(timedelta(hours=self._hours_period)))

    def draw(self, block=True) -> None:
        self._fig.show()
        # plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
        plt.show(block=block)

    def save_plot_to_png(self, file_name: Path) -> None:
        self._ax.axis('scaled')
        plt.savefig(file_name)

    @staticmethod
    def _add_legend_with_new_labels(new_labels: [str], new_label_colors: [Color], alpha: float, fontsize: int,
                                    title: str = None):
        if len(new_labels) != len(new_label_colors):
            raise ValueError('new_labels count must match new_label_colors count')
        else:
            plt.legend(handles=[Patch(label=new_labels[i], color=new_label_colors[i].get_rgb_with_alpha(alpha))
                                for i, label in enumerate(new_labels)],
                       loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, fontsize=fontsize, title=title)

    def _set_plot_limits(self):
        self._ax.set_ylim(0, len(self._row_names) * self._row_y_factor)
        self._ax.set_xlim(0, self._hours_period * MIN_IN_HOUR)

    def _set_xtick_locations_and_labels(self):
        xticks = np.arange(-1, self._hours_period + 1)
        self._ax.xaxis.set_major_locator(FixedLocator(xticks * MIN_IN_HOUR))
        self._ax.set_xticklabels(xticks)

    def _set_ytick_locations_and_labels(self):
        yticks = np.arange(0, len(self._row_names))
        self._ax.yaxis.set_major_locator(FixedLocator(yticks * self._row_y_factor))
        self._ax.yaxis.set_minor_locator(FixedLocator((yticks * self._row_y_factor) + (self._row_y_factor / 2)))
        self._ax.yaxis.set_major_formatter(NullFormatter())
        self._ax.yaxis.set_minor_formatter(FixedFormatter(self._row_names))
        self._ax.tick_params(axis='y', which='minor', labelsize=8)
        for tick in self._ax.yaxis.get_minor_ticks():
            tick.tick1line.set_markersize(0)
            tick.tick2line.set_markersize(0)

    def _set_alternating_row_color(self):
        row_color = Color.Grey
        for i, name in enumerate(self._row_names):
            if i % 2:
                self.set_row_color(i + 1, row_color, BACKGROUND_ALPHA / 2)

    def set_row_color(self, row_number: int, row_color: Color, alpha: float):
        self._ax.axhspan((row_number - 1) * self._row_y_factor, row_number * self._row_y_factor,
                         facecolor=row_color.get_rgb_with_alpha(alpha))

    def _calc_y(self, row: int, inner_row: int, bar_height: float) -> float:
        bar_center = bar_height / 2
        row_height = (row - 1) * self._row_y_factor
        bar_height_in_row = inner_row * bar_height
        y = row_height + bar_height_in_row + bar_center
        return y
