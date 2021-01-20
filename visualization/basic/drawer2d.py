from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto

from pathlib2 import Path

from geometry.geo2d import Point2D, Polygon2D, LineString2D, LinearRing2D
from visualization.basic.color import Color


class Drawer2DCoordinateSys(Enum):
    CARTESIAN = auto()
    GEOGRAPHIC = auto()


class Drawer2D(ABC):
    @abstractmethod
    def add_point2d(self, point2d: Point2D, radius=0.05, edgecolor: Color = Color.Blue, facecolor: Color = Color.Blue,
                    facecolor_alpha=1, linewidth=2, label=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_line_string2d(self, line_string2d: LineString2D, edgecolor: Color = Color.Green,
                          facecolor: Color = Color.White, linewidth=2, label=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_linear_ring2d(self, linear_ring2d: LinearRing2D, edgecolor: Color = Color.Yellow,
                          facecolor: Color = Color.Yellow, facecolor_alpha=0.2, linewidth=2, label=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_polygon2d(self, polygon2d: Polygon2D, edgecolor: Color = Color.Red, facecolor: Color = Color.Red,
                      facecolor_alpha=0.2, linewidth=2, label=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_arrow2d(self, tail: Point2D, head: Point2D, edgecolor: Color = Color.Black, facecolor: Color = Color.Black,
                    linewidth=2, label=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_text(self, text: str, point2d: Point2D, color: Color = Color.Black, fontsize: int = 10) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_legend(self, new_labels: [str] = None, new_label_colors: [Color] = None, fontsize: int = 10) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_plot_to_png(self, file_name: Path) -> None:
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
