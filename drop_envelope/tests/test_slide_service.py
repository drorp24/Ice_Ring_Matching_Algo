import unittest

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from drop_envelope.azimuth_quantization import get_azimuth_quantization_values
from drop_envelope.slide_service import _SlidesService
from geometry.geo2d import EmptyGeometry2D, Polygon2D


class BasicSlideServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.drop_azimuth_level_amount = 8
        cls.drone_azimuth_level_amount = 10
        cls.drop_azimuth_quantization_values = get_azimuth_quantization_values(cls.drop_azimuth_level_amount)
        cls.drone_azimuth_quantization_values = get_azimuth_quantization_values(cls.drone_azimuth_level_amount)
        cls.service = _SlidesService(cls.drop_azimuth_level_amount, cls.drone_azimuth_level_amount)

    def test_slide_service_creation(self):
        self.assertEqual(len(self.service.slide_container.slides), 640)
        self.assertIsInstance(self.service.get_slide(Angle(value=0, unit=AngleUnit.DEGREE),
                                                     Angle(value=135, unit=AngleUnit.DEGREE),
                                                     PackageType.TINY).internal_envelope, EmptyGeometry2D)
        self.assertIsInstance(self.service.get_slide(Angle(value=50, unit=AngleUnit.DEGREE),
                                                     Angle(value=90, unit=AngleUnit.DEGREE),
                                                     PackageType.TINY).internal_envelope, Polygon2D)
        self.assertIsInstance(self.service.get_slide(Angle(value=50, unit=AngleUnit.DEGREE),
                                                     Angle(value=50, unit=AngleUnit.DEGREE),
                                                     PackageType.TINY).internal_envelope, Polygon2D)
        self.assertEqual(self.service.get_slide(Angle(value=50, unit=AngleUnit.DEGREE),
                                                Angle(value=50, unit=AngleUnit.DEGREE),
                                                PackageType.TINY).drone_azimuth.degrees, 36)
