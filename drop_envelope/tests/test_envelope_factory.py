import unittest

from optional import Optional

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from drop_envelope.drop_envelope import DropEnvelope, DropEnvelopeProperties
from geometry.geo_factory import create_point_2d
from drop_envelope.envelope_factory import create_drop_envelope, create_potential_drop_envelope


class BasicSlideTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drop_point = create_point_2d(x=10, y=10)
        cls.package_type = PackageType.LARGE
        cls.drop_envelope_without_drop_azimuth = DropEnvelope(
            DropEnvelopeProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                   drop_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                   package_type=PackageType.LARGE,
                                   drop_point=create_point_2d(x=10, y=10)))

        cls.drop_envelope_with_drop_azimuth = DropEnvelope(
            DropEnvelopeProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                   drop_azimuth=Angle(value=40, unit=AngleUnit.DEGREE),
                                   package_type=PackageType.LARGE,
                                   drop_point=create_point_2d(x=10, y=10)))

    def test_create_drop_envelope(self):
        drone_azimuth = Angle(value=50, unit=AngleUnit.DEGREE)
        drop_envelope_without_drop_azimuth = create_drop_envelope(drop_azimuth=Optional.empty(),
                                                                  drone_azimuth=drone_azimuth,
                                                                  package_type=self.package_type,
                                                                  drop_point=self.drop_point)
        self.assertEqual(drop_envelope_without_drop_azimuth, self.drop_envelope_without_drop_azimuth)
        drop_envelope_with_drop_azimuth = create_drop_envelope(drop_azimuth=Optional.of(Angle(value=40, unit=AngleUnit.DEGREE)),
                                                               drone_azimuth=drone_azimuth,
                                                               package_type=self.package_type,
                                                               drop_point=self.drop_point)
        self.assertEqual(drop_envelope_with_drop_azimuth, self.drop_envelope_with_drop_azimuth)

    def test_create_potential_drop_envelopes(self):
        potential_drop_envelope_without_drop_azimuth = create_potential_drop_envelope(drop_azimuth=Optional.empty(),
                                                                                      package_type=self.package_type,
                                                                                      drop_point=self.drop_point)
        potential_drop_envelope_with_drop_azimuth = create_potential_drop_envelope(drop_azimuth=Optional.of(Angle(value=50, unit=AngleUnit.DEGREE)),
                                                                                   package_type=self.package_type,
                                                                                   drop_point=self.drop_point)
        self.assertEqual(len(potential_drop_envelope_with_drop_azimuth.envelopes), 3)
        self.assertEqual(len(potential_drop_envelope_without_drop_azimuth.envelopes), 8)
