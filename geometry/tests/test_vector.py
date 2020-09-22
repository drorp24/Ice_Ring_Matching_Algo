import unittest

from geometry.geo_factory import create_vector_2d


class BasicVectorTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.v1 = create_vector_2d(42, -42)

    def test_type(self):
        self.assertEqual(self.v1.type, 'Vector')

    def test_conversion_to_point(self):
        result = self.v1.to_point()
        self.assertEqual(result.type, 'Point')
        self.assertEqual((self.v1.x, self.v1.y), (result.x, result.y))


class BasicVectorMathTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.v1 = create_vector_2d(0, 42)
        cls.v2 = create_vector_2d(10, 3)

    def test_addition(self):
        result = self.v1.add(self.v2)
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, create_vector_2d(10, 45))

    def test_subtraction(self):
        result = self.v1.subtract(self.v2)
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, create_vector_2d(-10, 39))

    def test_int_multiplication(self):
        result = self.v1 * 2
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, create_vector_2d(0, 84))

    def test_float_multiplication(self):
        result = self.v1 * 1.01
        self.assertEqual(result.type, 'Vector')
        self.assertEqual(result, create_vector_2d(0, 42.42))

    def test_reversal(self):
        result = self.v2.reverse()
        self.assertEqual(result.type, 'Vector')
        self.assertEqual((result.x, result.y), (-10, -3))

    def test_dot(self):
        result = self.v1.dot(self.v2)
        self.assertTrue(isinstance(result, (int, float)))
        self.assertEqual(result, 126)

    def test_norm(self):
        result = self.v1.norm
        self.assertEqual(result, 42)
