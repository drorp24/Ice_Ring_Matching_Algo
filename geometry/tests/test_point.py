import unittest

from geometry.geo_factory import create_point_2d, create_vector_2d


class BasicPointTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(42, -42)

    def test_point_type(self):
        self.assertEqual(self.p1.type, 'Point')

    def test_point_conversion_to_vector(self):
        result = self.p1.to_vector()
        self.assertEqual(result.type, 'Vector')
        self.assertEqual((self.p1.x, self.p1.y), (result.x, result.y))


class BasicPointMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0, 0)
        cls.p2 = create_point_2d(10, 0)

    def test_point_addition(self):
        result = self.p1.add_vector(self.p2.to_vector())
        self.assertEqual(result.type, 'Point')
        self.assertEqual(result, create_point_2d(10, 0))

    def test_point_subtraction(self):
        result = self.p1.subtract_point(self.p2)
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, create_vector_2d(-10, 0))

    def test_point_distance(self):
        result = self.p1.calc_distance_to_point(self.p2)
        self.assertTrue(isinstance(result, float))
        self.assertEqual(result, 10)
