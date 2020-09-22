import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d


class BasicPolygonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 10.0)
        cls.p3 = create_point_2d(10.0, 10.0)
        cls.p4 = create_point_2d(10.0, 0.0)

        cls.p5 = create_point_2d(5.0, 11.0)
        cls.p6 = create_point_2d(4.0, 1.0)

        cls.poly1 = create_polygon_2d([cls.p1, cls.p2, cls.p3, cls.p4])
        cls.poly2 = create_polygon_2d([cls.p1, cls.p2, cls.p5, cls.p6])

    def test_type(self):
        self.assertEqual(self.poly1.type, 'Polygon')

    def test_points(self):
        points_result = self.poly1.points
        self.assertSetEqual(set(points_result), set([self.p1, self.p2, self.p3, self.p4]))
        self.assertEqual(points_result, list((self.p1, self.p2, self.p3, self.p4)))

    # def test_boundary(self):
    #     continue here
