import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d, create_linear_ring_2d, create_bbox
from geometry.utils import GeometryUtils


class BasicPolygonBboxTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(2.2, -25.1)
        cls.p2 = create_point_2d(2.2, 4.2)
        cls.p3 = create_point_2d(9.26, 4.2)
        cls.p4 = create_point_2d(9.26, -25.1)

        cls.min_point = create_point_2d(2.2, -25.1)
        cls.max_point  = create_point_2d(9.26, 4.2)

        cls.bbox = create_bbox(cls.min_point,cls.max_point)


    def test_type(self):
         self.assertEqual(self.bbox.type, 'Polygon')

    def test_points(self):
        points_result = self.bbox.points
        self.assertEqual(points_result, list((self.p1, self.p2, self.p3,self.p4)))

    def test_calc_area(self):
        area_result = self.bbox.calc_area()
        self.assertEqual(area_result, 206.858)


