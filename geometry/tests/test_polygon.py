import unittest

from geometry.geo2d import EmptyGeometry2D
from geometry.geo_factory import create_polygon_2d, create_point_2d, create_linear_ring_2d, create_multipolygon_2d
from geometry.shapely_wrapper import _ShapelyEmptyGeometry


class BasicPolygonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 10.0)
        cls.p3 = create_point_2d(10.0, 10.0)
        cls.p4 = create_point_2d(10.0, 0.0)
        cls.poly1 = create_polygon_2d([cls.p1, cls.p2, cls.p3, cls.p4])

    def test_type(self):
        self.assertEqual(self.poly1.type, 'Polygon')

    def test_points(self):
        points_result = self.poly1.points
        self.assertEqual(points_result, list((self.p1, self.p2, self.p3, self.p4)))

    def test_boundary(self):
        boundary = self.poly1.boundary
        self.assertEqual(boundary, create_linear_ring_2d([self.p1, self.p2, self.p3, self.p4]))

    def test_calc_area(self):
        area_result = self.poly1.calc_area()
        self.assertEqual(area_result, 100.0)


class PolygonOperationsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 5.0)
        cls.p3 = create_point_2d(5.0, 5.0)
        cls.p4 = create_point_2d(5.0, 0.0)

        cls.p5 = create_point_2d(3.0, 5.0)
        cls.p6 = create_point_2d(3.0, 0.0)

        cls.poly1 = create_polygon_2d([cls.p1, cls.p2, cls.p3, cls.p4])
        cls.poly2 = create_polygon_2d([cls.p1, cls.p2, cls.p5, cls.p6])

    def test_intersection(self):
        intersection_result = self.poly1.calc_intersection(self.poly2)
        self.assertEqual(intersection_result, self.poly2)

    def test_intersection_commutative(self):
        intersection_result_a = self.poly1.calc_intersection(self.poly2)
        intersection_result_b = self.poly2.calc_intersection(self.poly1)
        self.assertEqual(intersection_result_a, intersection_result_b)

    def test_difference(self):
        difference_result = self.poly1.calc_difference(self.poly2)
        expected_difference = create_polygon_2d([self.p5, self.p3, self.p4, self.p6])
        self.assertEqual(difference_result, expected_difference)

    def test_difference_with_empty_result(self):
        difference_result = self.poly1.calc_difference(self.poly1)
        expected_difference = EmptyGeometry2D()
        self.assertEqual(difference_result, expected_difference)

    def test_difference_with_multiple_polygon_output(self):
        wide_polygon = create_polygon_2d(
            [create_point_2d(0, 0), create_point_2d(0, 4), create_point_2d(10, 4), create_point_2d(10, 0)])
        tall_polygon = create_polygon_2d(
            [create_point_2d(5, -5), create_point_2d(5, 5), create_point_2d(6, 5), create_point_2d(6, -5)])
        multipolygon_expected_result = create_multipolygon_2d([
            create_polygon_2d([create_point_2d(0, 0),
                               create_point_2d(0, 4),
                               create_point_2d(5, 4),
                               create_point_2d(5, 0)]),
            create_polygon_2d([create_point_2d(6, 0),
                               create_point_2d(6, 4),
                               create_point_2d(10, 4),
                               create_point_2d(10, 0)])]
        )
        difference_result = wide_polygon.calc_difference(tall_polygon)
        self.assertEqual(difference_result, multipolygon_expected_result)
