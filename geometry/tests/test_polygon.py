import unittest

from geometry.geo_factory import create_polygon_2d, create_point_2d, create_linear_ring_2d, create_multipolygon_2d, \
    create_empty_geometry_2d


class BasicPolygonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 10.0)
        cls.p3 = create_point_2d(10.0, 10.0)
        cls.p4 = create_point_2d(10.0, 0.0)
        cls.poly1 = create_polygon_2d([cls.p1, cls.p2, cls.p3, cls.p4])

    def test_type(self):
        self.assertEqual(self.poly1._geo_type, 'Polygon')

    def test_points(self):
        points_result = self.poly1.points
        self.assertEqual(points_result, list((self.p1, self.p2, self.p3, self.p4)))

    def test_boundary(self):
        boundary = self.poly1.boundary()
        self.assertEqual(boundary, create_linear_ring_2d([self.p1, self.p2, self.p3, self.p4]))

    def test_calc_area(self):
        area_result = self.poly1.calc_area()
        self.assertEqual(area_result, 100.0)

    def test_creation_of_empty_polygon(self):
        self.assertRaises(AssertionError, create_polygon_2d, [])


class PolygonOperationsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        poly1_p1 = create_point_2d(0, 0)
        poly1_p2 = create_point_2d(0, 4)
        poly1_p3 = create_point_2d(10, 4)
        poly1_p4 = create_point_2d(10, 0)
        cls.poly1 = create_polygon_2d([poly1_p1, poly1_p2, poly1_p3, poly1_p4])

        poly2_p1 = create_point_2d(5, -5)
        poly2_p2 = create_point_2d(5, 5)
        poly2_p3 = create_point_2d(6, 5)
        poly2_p4 = create_point_2d(6, -5)
        cls.poly2 = create_polygon_2d([poly2_p1, poly2_p2, poly2_p3, poly2_p4])

        poly3_p1 = poly1_p1
        poly3_p2 = poly1_p2
        poly3_p3 = create_point_2d(5, 4)
        poly3_p4 = create_point_2d(5, 0)
        cls.poly3 = create_polygon_2d([poly3_p1, poly3_p2, poly3_p3, poly3_p4])

        pol4_p1 = create_point_2d(6, 0)
        poly4_p2 = create_point_2d(6, 4)
        poly4_p3 = poly1_p3
        poly4_p4 = poly1_p4
        cls.poly4 = create_polygon_2d([pol4_p1, poly4_p2, poly4_p3, poly4_p4])

        poly5_p1 = create_point_2d(5, 0)
        poly5_p2 = create_point_2d(5, 4)
        poly5_p3 = poly1_p3
        poly5_p4 = poly1_p4
        cls.poly5 = create_polygon_2d([poly5_p1, poly5_p2, poly5_p3, poly5_p4])

        poly6_p1 = create_point_2d(1, 1)
        poly6_p2 = create_point_2d(1, 2)
        poly6_p3 = create_point_2d(2, 2)
        poly6_p4 = create_point_2d(2, 1)
        cls.poly6 = create_polygon_2d([poly6_p1, poly6_p2, poly6_p3, poly6_p4])

    def test_contains(self):
        p1 = create_point_2d(2,2)
        p2 = create_point_2d(11,11)

        self.assertTrue(self.poly1.__contains__(p1))
        self.assertFalse(self.poly1.__contains__(p2))

    def test_intersection(self):
        intersection_result = self.poly1.calc_intersection(self.poly3)
        self.assertEqual(intersection_result, self.poly3)

    def test_intersection_commutative(self):
        intersection_result_a = self.poly1.calc_intersection(self.poly2)
        intersection_result_b = self.poly2.calc_intersection(self.poly1)
        self.assertEqual(intersection_result_a, intersection_result_b)

    def test_intersection_returns_empty(self):
        intersection_result = self.poly3.calc_intersection(self.poly5)
        expected_intersection = create_empty_geometry_2d()
        self.assertEqual(intersection_result, expected_intersection)

    def test_difference(self):
        difference_result = self.poly1.calc_difference(self.poly3)
        expected_difference = self.poly5
        self.assertEqual(difference_result, expected_difference)

    def test_difference_returns_empty(self):
        difference_result = self.poly1.calc_difference(self.poly1)
        expected_difference = create_empty_geometry_2d()
        self.assertEqual(difference_result, expected_difference)

    def test_difference_with_multiple_polygon_output(self):
        multipolygon_expected_result = create_multipolygon_2d([self.poly3, self.poly4])
        difference_result = self.poly1.calc_difference(self.poly2)
        self.assertEqual(difference_result, multipolygon_expected_result)

    # TODO implement Polygon2D.holes():
    #   def test_difference_with_hole_result(self):
    #     difference_result = self.poly1.calc_difference(self.poly6)
    #     expected_hole = create_linear_ring_2d(self.poly6.points)
    #     self.assertEqual(difference_result.holes[0], expected_hole)

    def test_union_with_self(self):
        union_result = self.poly1.calc_union(self.poly1)
        self.assertEqual(union_result, self.poly1)

    def test_union(self):
        union_result = self.poly5.calc_union(self.poly3)
        self.assertEqual(union_result, self.poly1)

    def test_union_with_multiple_polygon_output(self):
        union_result = self.poly3.calc_union(self.poly4)
        multipolygon_expected_result = create_multipolygon_2d([self.poly3, self.poly4])
        self.assertEqual(union_result, multipolygon_expected_result)
