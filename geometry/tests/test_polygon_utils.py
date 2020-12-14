import time
import unittest

from geometry.geo_factory import create_polygon_2d
from geometry.polygon_utils import PolygonUtils
from geometry.utils import GeometryUtils


class PolygonUtilsTestCase(unittest.TestCase):

    def test_split_polygon_simple_box_ra1_bs10(self):
        polygon_side_length = 10
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0, 0), (polygon_side_length, 0), (polygon_side_length, polygon_side_length), (0, polygon_side_length)]))
        required_area = 1
        box_resolution_list = [1, 2, 5, 10]
        for box_resolution in box_resolution_list:
            splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
            self.assertEqual(len(splited_polygon), polygon.calc_area() / box_resolution ** 2)

    def test_split_polygon_shifted_box_ra1_br1(self):
        polygon_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 0)

    def test_split_polygon_shifted_box_ra05_br1(self):
        polygon_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 0.5
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 0)

    def test_split_polygon_shifted_box_ra025_br1(self):
        polygon_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 0.25
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 4)

    def test_split_polygon_shifted_box_ra025_br1_negative_values(self):
        polygon_side_length = -1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 0.25
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 4)

    def test_split_polygon_large_box_ra1_br1_split_polygon(self):
        start_time = time.time()
        polygon_side_length = 10
        shift = 0
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        total_time = time.time() - start_time
        self.assertEqual(len(splited_polygon), polygon_side_length ** 2)
        self.assertLess(total_time, 0.2)

    def test_split_polygon_large_box_ra1_br1_negative_values(self):
        start_time = time.time()
        polygon_side_length = -10
        shift = 0
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, 0 + shift),
             (polygon_side_length + shift, polygon_side_length + shift), (0 + shift, polygon_side_length + shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        total_time = time.time() - start_time
        self.assertEqual(len(splited_polygon), polygon_side_length ** 2)
        self.assertLess(total_time, 0.2)

    def test_split_polygon_large_triangle1_ra1_br1(self):
        start_time = time.time()
        polygon_side_length = 10
        shift = 0
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
            [(0 + shift, 0 + shift), (polygon_side_length + shift, polygon_side_length + shift),
             (polygon_side_length + shift, 0 + shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon(polygon, box_resolution, required_area)
        total_time = time.time() - start_time
        self.assertLess(total_time, 0.2)
