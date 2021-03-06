from abc import ABC, abstractmethod

from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension
from visualization.basic.color import Color


class GanttDrawer(ABC):
    @abstractmethod
    def add_bar(self, row: int, time_window: TimeWindowExtension, name: str, time_mark: DateTimeExtension = None,
                side_text: str = None, color: Color = Color.Blue, inner_row: int = 0, max_inner_rows: int = 1) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_row_area(self, row: int, time_window: TimeWindowExtension,
                     facecolor: Color = Color.Red, face_alpha: float = 0,
                     edgecolor: Color = Color.Red) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_row_color(self, row_number: int, row_color: Color, alpha: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_legend(self, new_labels: [str] = None, new_label_colors: [Color] = None, alpha: float = None,
                   fontsize: int = 10, title: str = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_num_rows(self):
        raise NotImplementedError

    @abstractmethod
    def get_zero_time(self):
        raise NotImplementedError

    @abstractmethod
    def get_end_time(self):
        raise NotImplementedError

    @abstractmethod
    def draw(self, block=True) -> None:
        """
        Parameters
        ----------
        block : bool, optional

            If `True` block and run the GUI main loop until all windows
            are closed.

            If `False` ensure that all windows are displayed and return
            immediately.  In this case, you are responsible for ensuring
            that the event loop is running to have responsive figures.

            * Useful to draw multiple figures: all the drawers should not block except the last one.
        """

        raise NotImplementedError
