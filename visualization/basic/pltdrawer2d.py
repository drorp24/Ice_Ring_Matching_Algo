from typing import List

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle, PathPatch, Path, Patch

from geometry.geo2d import Point2D, Polygon2D, LineString2D, LinearRing2D
from visualization.basic.color import Color
from visualization.basic.drawer2d import Drawer2D, Drawer2DCoordinateSys

GEOGRAPHIC_RADIUS_SIZE_RATIO = 0.1


class MapImage:
    def __init__(self, map_background_path, west_lon, east_lon, south_lat, north_lat):
        self.map_background_path = map_background_path
        self.west_lon = west_lon
        self.east_lon = east_lon
        self.south_lat = south_lat
        self.north_lat = north_lat


def create_drawer_2d(coordinate_sys: Drawer2DCoordinateSys = Drawer2DCoordinateSys.CARTESIAN,
                     mapImage: MapImage = None) -> Drawer2D:
    return PltDrawer2D(coordinate_sys, mapImage)


class PltDrawer2D(Drawer2D):
    def __init__(self, coordinate_sys: Drawer2DCoordinateSys = Drawer2DCoordinateSys.CARTESIAN,
                 mapImage: MapImage = None):
        self._coordinate_sys = coordinate_sys
        self._init_according_to_coordinate_system(mapImage)
        self._patches_map = {}

    def add_point2d(self, point2d: Point2D, radius=0.05, edgecolor: Color = Color.Blue, facecolor: Color = Color.Blue,
                    facecolor_alpha=1, linewidth=2, label=None):
        if self._coordinate_sys is Drawer2DCoordinateSys.GEOGRAPHIC:
            radius *= GEOGRAPHIC_RADIUS_SIZE_RATIO
        point = Circle((point2d.x, point2d.y), radius=radius,
                       edgecolor=edgecolor.get_rgb(),
                       facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                       linewidth=linewidth, label=label)
        return self._ax.add_patch(point)

    def mpl_connect(self, patches_list, legend):
        for legline, origline in zip(legend.get_patches(), patches_list):
            legline.set_picker(True)
            self._patches_map[legline] = origline
        for legline, origline in self._patches_map.items():
            [axx.set_visible(False) for axx in origline]
            legline.set_alpha(0.2)
        def onpick(event):
            legline = event.artist
            origline = self._patches_map[legline]
            visible = all([not axx.get_visible() for axx in origline])
            [axx.set_visible(visible) for axx in origline]
            # Change the alpha on the line in the legend so we can see what lines
            # have been toggled.
            legline.set_alpha(1.0 if visible else 0.2)
            self._fig.canvas.draw()

        self._fig.canvas.mpl_connect('pick_event', onpick)

    def add_line_string2d(self, line_string2d: LineString2D, edgecolor: Color = Color.Green,
                          facecolor: Color = Color.White, linewidth=2, label=None) -> None:
        line_string = PathPatch(Path(self._convert_to_numpy_points(line_string2d.points)),
                                edgecolor=edgecolor.get_rgb(),
                                facecolor=facecolor.get_rgb(),
                                linewidth=linewidth, label=label)
        self._ax.add_patch(line_string)

    def add_linear_ring2d(self, linear_ring2d: LinearRing2D, edgecolor: Color = Color.Yellow,
                          facecolor: Color = Color.Yellow, facecolor_alpha=0.2, linewidth=2, label=None) -> None:
        linear_ring = PathPatch(Path(self._convert_to_numpy_points(linear_ring2d.points), closed=True),
                                edgecolor=edgecolor.get_rgb(),
                                facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                                linewidth=linewidth, label=label)
        self._ax.add_patch(linear_ring)

    def add_polygon2d(self, polygon2d: Polygon2D, edgecolor: Color = Color.Red, facecolor: Color = Color.Red,
                      facecolor_alpha=0.2, linewidth=2, label=None) -> None:
        polygon = Polygon(self._convert_to_numpy_points(polygon2d.points), closed=True,
                          edgecolor=edgecolor.get_rgb(),
                          facecolor=facecolor.get_rgb_with_alpha(facecolor_alpha),
                          linewidth=linewidth, label=label)
        self._ax.add_patch(polygon)

    def add_arrow2d(self, tail: Point2D, head: Point2D, edgecolor: Color = Color.Black, facecolor: Color = Color.Black,
                    linewidth=2, label=None) -> None:
        # Drawing transparent points so the annotation arrow will always be drawn even if outside axis
        self._ax.add_patch(Circle((tail.x, tail.y), radius=0.05, edgecolor=(1, 1, 1, 0), facecolor=(1, 1, 1, 0)))
        self._ax.add_patch(Circle((head.x, head.y), radius=0.05, edgecolor=(1, 1, 1, 0), facecolor=(1, 1, 1, 0)))

        self._ax.annotate("", xy=(head.x, head.y), xytext=(tail.x, tail.y), annotation_clip=False,
                          arrowprops=dict(arrowstyle='->', edgecolor=edgecolor.get_rgb(),
                                          facecolor=facecolor.get_rgb(), linewidth=linewidth, label=label))

    def add_text(self, text: str, point2d: Point2D, color: Color = Color.Black, fontsize: int = 10) -> None:
        self._ax.text(point2d.x, point2d.y, text, color=color.get_rgb(), fontsize=fontsize)

    def add_legend(self, new_labels: [str] = None, new_label_colors: [Color] = None, fontsize: int = 10, patches_list = None) -> None:
        if new_labels is not None:
            leg = self._add_legend_with_new_labels(new_labels, new_label_colors, fontsize)
        else:
            leg = plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left", ncol=3)
        if patches_list is not None:
            self.mpl_connect(patches_list=patches_list, legend=leg)

    def draw(self, block=True) -> None:
        self._ax.axis('scaled')
        if self._coordinate_sys is Drawer2DCoordinateSys.CARTESIAN:
            self._fig.tight_layout()
        self._fig.show()
        plt.show(block=block)

    def save_plot_to_png(self, file_name: Path) -> None:
        self._ax.axis('scaled')
        if self._coordinate_sys is Drawer2DCoordinateSys.CARTESIAN:
            self._fig.tight_layout()
        plt.savefig(file_name)

    def _init_according_to_coordinate_system(self, mapImage: MapImage):
        if self._coordinate_sys is Drawer2DCoordinateSys.CARTESIAN:
            self._fig, self._ax = plt.subplots()
            plt.title('90\xb0', fontsize=14)
            plt.xlabel('270\xb0', fontsize=14)
            plt.ylabel('180\xb0', fontsize=14)
        elif self._coordinate_sys is Drawer2DCoordinateSys.GEOGRAPHIC:
            self._fig = plt.figure()
            self._ax = plt.axes(projection=ccrs.PlateCarree())
            if mapImage is not None:
                map_background_path = mapImage.map_background_path
                west_lon = mapImage.west_lon
                east_lon = mapImage.east_lon
                south_lat = mapImage.south_lat
                north_lat = mapImage.north_lat

                map_background_img_extent = (west_lon,
                                             east_lon,
                                             south_lat,
                                             north_lat)
                map_background_img = plt.imread(map_background_path)
                self._ax.imshow(map_background_img, origin='upper', extent=map_background_img_extent,
                                transform=ccrs.PlateCarree())
        else:
            raise NotImplementedError("Non valid Drawer2DCoordinateSys.")

    @staticmethod
    def _convert_to_numpy_points(point2d_list: List[Point2D]) -> np.ndarray:
        np_points = np.zeros(shape=(len(point2d_list), 2))
        for i, point in enumerate(point2d_list):
            np_points[i] = [point.x, point.y]
        return np_points

    @staticmethod
    def _add_legend_with_new_labels(new_labels: [str], new_label_colors: [Color], fontsize: int):
        if len(new_labels) != len(new_label_colors):
            raise ValueError('new_labels count must match new_label_colors count')
        else:
            return plt.legend(fancybox=True, shadow=True,handles=[
                Patch(label=new_labels[i], color=new_label_colors[i].get_rgb()) for i, label in enumerate(new_labels)],
                      loc="upper left", bbox_to_anchor=(1.01, 1), ncol=3, fontsize=fontsize)
