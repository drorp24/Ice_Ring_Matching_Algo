import unittest

from geometry.geo_factory import create_point_2d
from geometry.geometry_utils import GeometryUtils


class GeometryUtilsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.point_list = [create_point_2d(2.2, 3), create_point_2d(6, 5.5), create_point_2d(4, 1.2)]
        cls.xy_array = [(2.2, 3), (6, 5.5), (4, 1.2)]
        cls.x_array, cls.y_array = [2.2, 6, 4], [3, 5.5, 1.2]

    def test_conversion_xy_array_to_point_list(self):
        point_list_result = GeometryUtils.convert_xy_array_to_points_list(self.xy_array)
        self.assertEqual(point_list_result, self.point_list)

    def test_conversion_xy_separate_arrays_to_point_list(self):
        point_list_result = GeometryUtils.convert_xy_separate_arrays_to_points_list(self.x_array, self.y_array)
        self.assertEqual(point_list_result, self.point_list)

    def test_conversion_points_list_to_xy_array(self):
        point_list_converted_result = GeometryUtils.convert_points_list_to_xy_array(self.point_list)
        self.assertEqual(point_list_converted_result, self.xy_array)
