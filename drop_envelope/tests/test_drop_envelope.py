import unittest

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from drop_envelope.drop_envelope import DropEnvelopeProperties, DropEnvelope
from geometry.geo_factory import create_point_2d


class BasicDropEnvelopeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drop_envelope_properties_1 = DropEnvelopeProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                                drop_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                                package_type=PackageType.LARGE,
                                                                drop_point=create_point_2d(x=10, y=10))

        cls.drop_envelope_properties_2 = DropEnvelopeProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                                drop_azimuth=Angle(value=90, unit=AngleUnit.DEGREE),
                                                                package_type=PackageType.LARGE,
                                                                drop_point=create_point_2d(x=10, y=10))

    def test_create_drop_envelope_without_drop_azimuth(self):
        drop_envelope = DropEnvelope(drop_envelope_properties=self.drop_envelope_properties_1)
        self.assertEqual(drop_envelope.drop_point, create_point_2d(x=10, y=10))
        self.assertAlmostEqual(drop_envelope.calc_location().x, -73.96893026590254)
        self.assertAlmostEqual(drop_envelope.calc_location().y, -73.96893026590254)

    def test_create_drop_envelope_with_drop_azimuth(self):
        drop_envelope = DropEnvelope(drop_envelope_properties=self.drop_envelope_properties_2)
        self.assertEqual(drop_envelope.drop_point, create_point_2d(x=10, y=10))
