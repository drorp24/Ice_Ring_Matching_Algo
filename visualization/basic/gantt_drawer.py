from abc import ABC, abstractmethod

from common.entities.temporal import DateTimeExtension, TimeWindowExtension
from visualization.basic.color import Color


class GanttDrawer(ABC):
    @abstractmethod
    def add_bar(self, row: int, time_window: TimeWindowExtension, name: str, time_mark: DateTimeExtension = None,
                color: Color = Color.Blue) -> None:
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
