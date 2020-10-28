import unittest

from services.mock_envelope_services import MockEnvelopeServices


class BasicSlideTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.envelope_service = MockEnvelopeServices()

    def test_type(self):
        self.assertEqual(self.p1.type, 'Point')

    def test_conversion_to_vector(self):
        result = self.p1.to_vector()
        self.assertEqual(result.type, 'Vector')
        self.assertEqual((self.p1.x, self.p1.y), (result.x, result.y))


