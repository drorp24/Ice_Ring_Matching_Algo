import unittest

from geometry.geo_factory import Geo2D


class BasicVectorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.v1 = Geo2D.create_vector_2d(42, -42)

    def test_vector_type(self):
        self.assertEqual(self.v1.type, 'Vector')

    def test_vector_conversion_to_point(self):
        result = self.v1.to_point()
        self.assertEqual(result.type, 'Point')
        self.assertEqual((self.v1.x, self.v1.y), (result.x, result.y))


class BasicVectorMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.v1 = Geo2D.create_vector_2d(0, 42)
        cls.v2 = Geo2D.create_vector_2d(10, 3)

    def test_vector_addition(self):
        result = self.v1.add_vector(self.v2)
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, Geo2D.create_vector_2d(10, 45))

    def test_vector_subtraction(self):
        result = self.v1.subtract_vector(self.v2)
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, Geo2D.create_vector_2d(-10, 39))

    def test_vector_vector_multiplication(self):
        result = self.v1 * self.v2
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, Geo2D.create_vector_2d(0, 126))

    def test_vector_int_multiplication(self):
        result = self.v1 * 2
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, Geo2D.create_vector_2d(0, 84))

    def test_vector_float_multiplication(self):
        result = self.v1 * 1.01
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, Geo2D.create_vector_2d(0, 42.42))

    def test_vector_reversal(self):
        result = self.v2.reverse_vector()
        self.assertEqual(result.type, 'Vector')
        self.assertEqual((result.x, result.y), (-10, -3))

    def test_vector_dot(self):
        result = self.v1.dot_product(self.v2)
        self.assertTrue(isinstance(result, (int, float)))
        self.assertEqual(result, 126)
