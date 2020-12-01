import unittest

from geometry.geo_factory import create_point_2d, create_vector_2d, calc_centroid


class BasicPointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(42, -42)

    def test_type(self):
        self.assertEqual(self.p1._geo_type, 'Point')

    def test_conversion_to_vector(self):
        result = self.p1.to_vector()
        self.assertEqual(result._geo_type, 'Vector')
        self.assertEqual((self.p1.x, self.p1.y), (result.x, result.y))


class BasicPointMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0, 0)
        cls.p2 = create_point_2d(10, 0)

    def test_addition(self):
        result = self.p1.add_vector(self.p2.to_vector())
        self.assertEqual(result._geo_type, 'Point')
        self.assertEqual(result, create_point_2d(10, 0))

    def test_subtraction(self):
        result = self.p1.subtract(self.p2)
        self.assertEqual(result._geo_type, 'Vector')
        self.assertEqual(result, create_vector_2d(-10, 0))

    def test_distance(self):
        result = self.p1.calc_distance_to_point(self.p2)
        self.assertTrue(isinstance(result, float))
        self.assertEqual(result, 10)

    def test_calc_centroid(self):
        result = calc_centroid(points=[self.p1, self.p1, self.p1, self.p2])
        self.assertEqual(create_point_2d(2.5, 0), result)

    def test_calc_centroid_on_single_point(self):
        result = calc_centroid(points=[self.p1])
        self.assertEqual(self.p1, result)
