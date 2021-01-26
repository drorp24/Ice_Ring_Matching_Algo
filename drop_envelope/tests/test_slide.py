import unittest

from common.entities.base_entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from drop_envelope.slide import Slide, SlideProperties
from geometry.geo_factory import create_point_2d
from services.mock_envelope_services import MockEnvelopeServices


class BasicSlideTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.slide_properties_1 = SlideProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                 drop_azimuth=Angle(value=40, unit=AngleUnit.DEGREE),
                                                 package_type=PackageType.LARGE)
        cls.slide_properties_2 = SlideProperties(drone_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                 drop_azimuth=Angle(value=50, unit=AngleUnit.DEGREE),
                                                 package_type=PackageType.LARGE)
        cls.envelope_service = MockEnvelopeServices()

    def test_build_slide(self):
        slide = Slide(self.slide_properties_1, self.envelope_service)
        self.assertEqual(round(slide.calc_area(), 4), 120.0864)
        self.assertEqual(slide.drop_azimuth.degrees, 40)
        self.assertEqual(slide.drone_azimuth.degrees, 50)
        self.assertEqual(slide.package_type, PackageType.LARGE)

    def test_slide_shift(self):
        slide = Slide(self.slide_properties_2, self.envelope_service)
        shifted_slide_polygon = slide.shift(create_point_2d(x=10.0, y=10.0))
        shifted_polygon = slide.shift(create_point_2d(x=10.0, y=10.0))
        self.assertEqual(shifted_polygon, shifted_slide_polygon)
