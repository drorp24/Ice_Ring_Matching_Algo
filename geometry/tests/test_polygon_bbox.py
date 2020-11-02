import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d, create_linear_ring_2d, create_bbox
from geometry.geometry_utils import GeometryUtils


class BasicPolygonBboxTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.min_x, cls.min_y, cls.max_x, cls.max_y = 2.2, -25.1, 9.26, 4.2
        cls.bbox = create_bbox(cls.min_x, cls.min_y, cls.max_x, cls.max_y)

        cls.p1 = create_point_2d(cls.max_x, cls.min_y)
        cls.p2 = create_point_2d(cls.max_x, cls.max_y)
        cls.p3 = create_point_2d(cls.min_x, cls.max_y)
        cls.p4 = create_point_2d(cls.min_x, cls.min_y)

    def test_type(self):
         self.assertEqual(self.bbox.type, 'Polygon')

    def test_points(self):
        points_result = self.bbox.points
        self.assertEqual(points_result, list((self.p1, self.p2, self.p3,self.p4)))

    def test_calc_area(self):
        area_result = self.bbox.calc_area()
        self.assertEqual(area_result, 206.858)


