from datetime import datetime
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

from common.entities.temporal import DateTimeExtension, TimeWindowExtension
from visualization.basic.color import Color
from visualization.basic.gantt_drawer import GanttDrawer


def create_gantt_drawer(zero_time: DateTimeExtension, hours_period: int, num_rows: int) -> GanttDrawer:
    return PltGanttDrawer(zero_time, hours_period, num_rows)

BAR_HEIGHT_RATIO = 0.1
MARK_WIDTH_RATIO = 0.4
YLIMIT = 100
ALPHA = 0.6

class PltGanttDrawer(GanttDrawer):
    def __init__(self, zero_time: DateTimeExtension, hours_period: int, num_rows: int):
        self._zero_time = zero_time
        self._hours_period = hours_period
        self._fig, self._ax = plt.subplots()
        self._counters = np.zeros(num_rows)
        self._row_y_factor = YLIMIT / num_rows
        self._bar_height = self._row_y_factor * BAR_HEIGHT_RATIO

        # Setting Y-axis limits
        self._ax.set_ylim(0, num_rows * self._row_y_factor)

        # Setting X-axis limits
        self._ax.set_xlim(0, hours_period * 60)

        # Setting labels for x-axis and y-axis
        self._ax.set_xlabel('Minutes since ' + self._zero_time.get_internal().strftime("%d/%m/%Y %H:%M:%S"))
        # self._ax.set_ylabel('Processor')

        self._ax.xaxis.set_major_locator(MultipleLocator(60))
        self._ax.yaxis.set_major_locator(MultipleLocator(self._row_y_factor))
        self._ax.set_xticklabels(np.arange(-1, hours_period + 1))
        self._ax.grid(b=True)

    def _calc_y(self, row: int) -> float:
        # To prevent bars override we change their height
        y = row * self._row_y_factor - self._row_y_factor * 0.3 + self._counters[row] * self._bar_height % (
                    self._row_y_factor * 0.6)
        self._counters[row] += 1
        return y

    def add_bar(self, row: int, time_window: TimeWindowExtension, name: str, time_mark: DateTimeExtension = None, color: Color=Color.Blue) -> None:
        since, until = time_window.get_relative_time_in_min(self._zero_time)
        y = self._calc_y(row)
        self._ax.barh(y=y, width=until - since, height=self._bar_height, left=since, color=color.get_rgb_with_alpha(ALPHA), label=name)
        if time_mark:
            relative_time_in_min = time_mark.get_time_delta(self._zero_time).in_minutes()
            width = MARK_WIDTH_RATIO * self._hours_period
            self._ax.barh(y=y, width=width, height=self._bar_height, left=relative_time_in_min, color=color.Black.get_rgb())

    def add_row_name(self, row: int, name: str) -> None:
        tick_labels = self._ax.get_yticklabels()
        tick_labels[row + 1] = name
        self._ax.set_yticklabels(tick_labels)

    def draw(self, block=True) -> None:
        # self._ax.axis('scaled')
        self._fig.show()
        plt.legend(bbox_to_anchor=(1.01,1), loc="upper left")
        plt.show(block=block)

    def save_plot_to_png(self, file_name: Path) -> None:
        self._ax.axis('scaled')
        plt.savefig(file_name)


zero_time = DateTimeExtension.from_dt(datetime(2020, 1, 23, 0, 00, 00))
hours_period = 24
drawer = create_gantt_drawer(zero_time=zero_time, hours_period=hours_period, num_rows=10)
tw1 = TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 16, 00, 00)))
drawer.add_bar(row=1, time_window=tw1, name='x1', time_mark=DateTimeExtension.from_dt(datetime(2020, 1, 23, 14, 30, 00)), color=Color.Blue)
drawer.add_row_name(1, 'tw1')
tw2 = TimeWindowExtension(
                since=DateTimeExtension.from_dt(datetime(2020, 1, 23, 13, 30, 00)),
                until=DateTimeExtension.from_dt(datetime(2020, 1, 23, 16, 00, 00)))
drawer.add_bar(row=1, time_window=tw1, name='x2', color=Color.Green)
drawer.add_bar(row=1, time_window=tw1, name='x3', color=Color.Yellow)
drawer.add_bar(row=1, time_window=tw1, name='x4', color=Color.Purple)
drawer.add_bar(row=1, time_window=tw1, name='x5', color=Color.Red)
drawer.add_row_name(2, 'tw2')
drawer.draw()
