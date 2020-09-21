import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d


class BasicPointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 10.0)
        cls.p3 = create_point_2d(10.0, 10.0)
        cls.p4 = create_point_2d(10.0, 0.0)

        cls.p5 = create_point_2d(5.0, 11.0)
        cls.p6 = create_point_2d(4.0, 1.0)

        point_list = list([cls.p1, cls.p2, cls.p3, cls.p4])
        cls.poly1 = create_polygon_2d(point_list)
        cls.poly2 = create_polygon_2d([cls.p1, cls.p2, cls.p5, cls.p6])

    def test_point_type(self):
        self.assertEqual(self.poly1.type, 'Polygon')
        p = self.poly1.calc_intersection(self.poly2)
        self.assertTrue(p.calc_area() > 0)
