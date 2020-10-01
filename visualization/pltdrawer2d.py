import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, PathPatch, Path
from typing import List

from visualization.drawer2d import Drawer2D
from visualization.color import Color
from geometry.geo2d import Point2D, Polygon2D, LineString2D, LinearRing2D


class PltDrawer2D(Drawer2D):
    def __init__(self):
        self._fig, self._ax = plt.subplots()

    @staticmethod
    def _convert_to_numpy_points(point2d_list: List[Point2D]) -> np.ndarray:
        np_points = np.zeros(shape=(len(point2d_list), 2))
        for i, point in enumerate(point2d_list):
            np_points[i] = [point.x, point.y]
        return np_points

    def add_point2d(self, point2d: Point2D, radius=0.05, edgecolor: Color = Color.Blue, facecolor: Color = Color.Blue,
                    facecolor_alpha=1, linewidth=2) -> None:
        point = Circle((point2d.x, point2d.y), radius=radius,
                       edgecolor=edgecolor.get_rgb(),
                       facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                       linewidth=linewidth)
        self._ax.add_patch(point)

    def add_line_string2d(self, line_string2d: LineString2D, edgecolor: Color = Color.Green,
                          facecolor: Color = Color.White, linewidth=2) -> None:
        line_string = PathPatch(Path(self._convert_to_numpy_points(line_string2d.points)),
                                edgecolor=edgecolor.get_rgb(),
                                facecolor=facecolor.get_rgb(),
                                linewidth=linewidth)
        self._ax.add_patch(line_string)

    def add_linear_ring2d(self, linear_ring2d: LinearRing2D, edgecolor: Color = Color.Yellow,
                          facecolor: Color = Color.Yellow, facecolor_alpha=0.2, linewidth=2) -> None:
        linear_ring = PathPatch(Path(self._convert_to_numpy_points(linear_ring2d.points), closed=True),
                                edgecolor=edgecolor.get_rgb(),
                                facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                                linewidth=linewidth)
        self._ax.add_patch(linear_ring)

    def add_polygon2d(self, polygon2d: Polygon2D, edgecolor: Color = Color.Red, facecolor: Color = Color.Red,
                      facecolor_alpha=0.2, linewidth=2) -> None:
        polygon = Polygon(self._convert_to_numpy_points(polygon2d.points), closed=True,
                          edgecolor=edgecolor.get_rgb(),
                          facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                          linewidth=linewidth)
        self._ax.add_patch(polygon)

    def draw(self) -> None:
        self._ax.axis('scaled')
        plt.show()

    def save_plot_to_png(self, file_name: Path) -> None:
        self._ax.axis('scaled')
        plt.savefig(file_name)
