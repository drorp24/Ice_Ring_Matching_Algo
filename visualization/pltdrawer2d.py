import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, PathPatch, Path
from typing import List

from visualization.drawer2d import Drawer2D
from geometry.geo2d import Point2D, Vector2D, Polygon2D, LineString2D, LinearRing2D


def change_color_alpha(color, alpha):
    new_color = (color[0], color[1], color[2], alpha)
    return new_color


def convert_to_numpy_points(point2d_list: List[Point2D]) -> np.ndarray:
    np_points = np.zeros(shape=(len(point2d_list), 2))
    for i, point in enumerate(point2d_list):
        np_points[i] = [point.x, point.y]
    return np_points


class PltDrawer2D(Drawer2D):
    def __init__(self):
        self._fig, self._ax = plt.subplots()

    def add_point2d(self, point2d: Point2D, edgecolor='blue', facecolor='blue', linewidth=2):
        point = Circle((point2d.x, point2d.y), radius=0.05, edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)
        transparent_facecolor = change_color_alpha(point.get_facecolor(), 1)
        point.set_facecolor(transparent_facecolor)
        self._ax.add_patch(point)

    def add_vector2d(self, vector2d: Vector2D, edgecolor='blue', facecolor='blue', linewidth=2):
        self.add_point2d(vector2d.to_point(), edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)

    def add_line_string2d(self, line_string2d: LineString2D, edgecolor='green', facecolor='white', linewidth=2):
        line_string = PathPatch(Path(convert_to_numpy_points(line_string2d.points)), edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)
        self._ax.add_patch(line_string)

    def add_linear_ring2d(self, linear_ring2d: LinearRing2D, edgecolor='yellow', facecolor='yellow', linewidth=2):
        linear_ring = PathPatch(Path(convert_to_numpy_points(linear_ring2d.points), closed=True), edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)
        transparent_facecolor = change_color_alpha(linear_ring.get_facecolor(), 0.2)
        linear_ring.set_facecolor(transparent_facecolor)
        self._ax.add_patch(linear_ring)

    def add_polygon2d(self, polygon2d: Polygon2D, edgecolor='red', facecolor='red', linewidth=2):
        polygon = Polygon(convert_to_numpy_points(polygon2d.points), closed=True, edgecolor=edgecolor, facecolor=facecolor, linewidth=linewidth)
        transparent_facecolor = change_color_alpha(polygon.get_facecolor(), 0.2)
        polygon.set_facecolor(transparent_facecolor)
        self._ax.add_patch(polygon)

    def add_arrow2d(self, tail: Point2D, head: Point2D):
        self._ax.annotate("", xy=(head.x, head.y), xytext=(tail.x, tail.y), arrowprops=dict(arrowstyle="->"))

    def draw(self):
        self._ax.axis('scaled')
        plt.show()

    def save_plot_to_png(self, file_name):
        self._ax.axis('scaled')
        plt.savefig(file_name)
