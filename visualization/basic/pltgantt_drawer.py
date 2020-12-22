from datetime import timedelta
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullFormatter, FixedFormatter

from common.entities.temporal import DateTimeExtension, TimeWindowExtension, MIN_IN_HOUR, TimeDeltaExtension
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer

BARS_IN_ROW = 5
BAR_HEIGHT_RATIO = 1 / BARS_IN_ROW
MARK_WIDTH_RATIO = 0.1
YLIMIT = 100
BAR_ALPHA = 0.6
BACKGROUND_ALPHA = 0.1


def create_gantt_drawer(zero_time: DateTimeExtension, hours_period: int, row_names: [str],
                        rows_title: str) -> GanttDrawer:
    return PltGanttDrawer(zero_time, hours_period, row_names, rows_title)


class PltGanttDrawer(GanttDrawer):
    def __init__(self, zero_time: DateTimeExtension, hours_period: int, row_names: [str], rows_title: str):
        self._zero_time = zero_time
        self._hours_period = hours_period
        self._fig, self._ax = plt.subplots()
        self._row_names = row_names
        self._rows_title = rows_title
        self._counters = np.zeros(len(row_names))
        self._row_y_factor = YLIMIT / len(row_names)
        self._bar_height = self._row_y_factor * BAR_HEIGHT_RATIO

        self._set_plot_limits()
        self._set_xtick_locations_and_labels()
        self._set_ytick_locations_and_labels()
        self._set_alternating_row_color()
        self._ax.set_xlabel('Hours since ' + self._zero_time.str_format_time())
        self._ax.set_ylabel(rows_title, labelpad=10)
        self._ax.grid(b=True)

    def add_bar(self, row: int, time_window: TimeWindowExtension, name: str, time_mark: DateTimeExtension = None,
                side_text: str = None, color: Color = Color.Blue) -> None:
        since, until = time_window.get_relative_time_in_min(self._zero_time)
        y = self._calc_y(row)
        self._ax.barh(y=y, width=until - since, height=self._bar_height, left=since,
                      color=color.get_rgb_with_alpha(BAR_ALPHA), label=name,
                      edgecolor=Color.Black.get_rgb(), linewidth=1)
        if side_text:
            self._ax.text(x=until + MARK_WIDTH_RATIO * self._hours_period, y=y - self._bar_height / 2, s=side_text,
                          color=Color.Black.get_rgb(), fontsize=9)
        if time_mark:
            relative_time_in_min = time_mark.get_time_delta(self._zero_time).in_minutes()
            width = MARK_WIDTH_RATIO * self._hours_period
            self._ax.barh(y=y, width=width, height=self._bar_height, left=relative_time_in_min - width / 2,
                          color=color.Black.get_rgb())

    def add_row_area(self, row: int, time_window: TimeWindowExtension,
                     facecolor: Color = Color.Red, face_alpha: float = 0,
                     edgecolor: Color = Color.Red) -> None:
        since, until = time_window.get_relative_time_in_min(self._zero_time)
        y = (row - 1) * self._row_y_factor + self._row_y_factor / 2
        self._ax.barh(y=y, width=until - since, height=self._row_y_factor, left=since,
                      facecolor=facecolor.get_rgb_with_alpha(face_alpha),
                      edgecolor=edgecolor.get_rgb(),
                      linewidth=1)

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
        for i, name in enumerate(self._row_names):
            if i % 2:
                self._ax.axhspan(i * self._row_y_factor, (i + 1) * self._row_y_factor,
                                 facecolor=Color.Grey.get_rgb_with_alpha(BACKGROUND_ALPHA / 2))

    def _calc_y(self, row: int) -> float:
        # To prevent bars override we change their height
        bar_center = self._bar_height / 2
        row_height = (row - 1) * self._row_y_factor
        bar_height_in_row = self._counters[row - 1] * self._bar_height
        y = row_height + bar_height_in_row + bar_center
        self._counters[row - 1] = (self._counters[row - 1] + 1) % BARS_IN_ROW
        return y

# zero_time = DateTimeExtension.from_dt(datetime(2020, 1, 23, 0, 00, 00))
# hours_period = 24
# row_names = ['row1', 'row2', 'row3', 'row4', 'row5']
# drawer = create_gantt_drawer(zero_time=zero_time, hours_period=hours_period, row_names=row_names)
# tw1 = TimeWindowExtension(
#     since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 30, 00)),
#     until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 16, 00, 00)))
# drawer.add_bar(row=1, time_window=tw1, name='x1',
#                time_mark=DateTimeExtension.from_dt(datetime(2020, 1, 23, 14, 30, 00)), color=Color.Blue)
# tw2 = TimeWindowExtension(
#     since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 15, 30, 00)),
#     until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 18, 00, 00)))
# drawer.add_bar(row=1, time_window=tw1, name='x2', color=Color.Green)
# drawer.add_bar(row=1, time_window=tw1, name='x3', color=Color.Yellow)
# drawer.add_bar(row=1, time_window=tw1, name='x4', color=Color.Purple)
# drawer.add_bar(row=1, time_window=tw1, name='x5', color=Color.Red)
# drawer.add_bar(row=2, time_window=tw1, name='x6', color=Color.Aquamarine)
# drawer.add_bar(row=2, time_window=tw1, name='x7', color=Color.Brown)
# drawer.add_bar(row=2, time_window=tw2, name='x8',
#                time_mark=DateTimeExtension.from_dt(datetime(2020, 1, 23, 17, 30, 00)), color=Color.Cyan)
# drawer.add_bar(row=2, time_window=tw1, name='x9', color=Color.DarkTurquoise)
# drawer.add_bar(row=3, time_window=tw1, name='x10', color=Color.Grey)
# drawer.add_bar(row=3, time_window=tw1, name='x11', color=Color.Indigo)
# drawer.add_bar(row=4, time_window=tw2, name='x12', color=Color.Pink)
# drawer.add_bar(row=5, time_window=tw2, name='x13', color=Color.Lime)
# drawer.draw()
