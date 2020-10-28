import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d
from geometry.utils import GeometryUtils, PolygonUtils


class PolygonUtilsTestCase(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):


    def test_split_polygon_simple_box_ra1_bs10(self):
        box_side_length = 10
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0, 0), (box_side_length,0), (box_side_length,box_side_length), (0,box_side_length)]))
        required_area = 1
        box_resolution_list = [1,2,5,10]
        for box_resolution in box_resolution_list:
            splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
            self.assertEqual(len(splited_polygon), polygon.calc_area()/box_resolution**2)

    def test_split_polygon_shifted_box_ra1_br1(self):
        box_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0+shift, 0+shift), (box_side_length+shift,0+shift), (box_side_length+shift,box_side_length+shift), (0+shift,box_side_length+shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon),0)

    def test_split_polygon_shifted_box_ra05_br1(self):
        box_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0+shift, 0+shift), (box_side_length+shift,0+shift), (box_side_length+shift,box_side_length+shift), (0+shift,box_side_length+shift)]))
        required_area = 0.5
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 0)


    def test_split_polygon_shifted_box_ra1_br1(self):
        box_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0+shift, 0+shift), (box_side_length+shift,0+shift), (box_side_length+shift,box_side_length+shift), (0+shift,box_side_length+shift)]))
        required_area = 0.25
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 4)


    def test_split_polygon_shifted_box_ra025_br1(self):
        box_side_length = 1
        shift = 0.5
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0+shift, 0+shift), (box_side_length+shift,0+shift), (box_side_length+shift,box_side_length+shift), (0+shift,box_side_length+shift)]))
        required_area = 0.25
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 4)

    def test_split_polygon_large_box_ra1_br1(self):
        box_side_length = 100
        shift = 0
        polygon = create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list([(0+shift, 0+shift), (box_side_length+shift,0+shift), (box_side_length+shift,box_side_length+shift), (0+shift,box_side_length+shift)]))
        required_area = 1
        box_resolution = 1
        splited_polygon = PolygonUtils.split_polygon1(polygon, box_resolution, required_area)
        self.assertEqual(len(splited_polygon), 1000*1000)

