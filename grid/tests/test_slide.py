import unittest

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.slide import Slide, SlideProperties
from grid.slides_factory import create_slide, generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicSlideTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.envelope_service = MockEnvelopeServices()
        cls.drone_azimuth = Angle(90, AngleUnit.DEGREE)
        cls.drop_azimuth = Angle(45, AngleUnit.DEGREE)
        cls.cell_width_resolution = 1
        cls.cell_height_resolution = 2
        cls.cell_required_area = 0.5
        cls.drone_azimuth_resolution = 8
        cls.drop_azimuth_resolution = 8

        cls.slide_properties_tiny = SlideProperties(envelope_service=MockEnvelopeServices(),
                                                    package_type=PackageType.TINY,
                                                    drone_azimuth=cls.drone_azimuth,
                                                    drop_azimuth=cls.drop_azimuth,
                                                    cell_width_resolution=cls.cell_width_resolution,
                                                    cell_height_resolution=cls.cell_height_resolution,
                                                    cell_required_area=cls.cell_required_area)

        cls.slide_properties_medium = SlideProperties(envelope_service=MockEnvelopeServices(),
                                                      package_type=PackageType.MEDIUM,
                                                      drone_azimuth=cls.drone_azimuth,
                                                      drop_azimuth=cls.drop_azimuth,
                                                      cell_width_resolution=cls.cell_width_resolution,
                                                      cell_height_resolution=cls.cell_height_resolution,
                                                      cell_required_area=cls.cell_required_area)

        cls.slide1 = create_slide(cls.slide_properties_tiny)

        cls.slide2 = create_slide(cls.slide_properties_medium)

        cls.package_types = [package_type for package_type in PackageType]
        cls.slides_container = generate_slides_container(cls.envelope_service,
                                                         cls.package_types,
                                                         cls.drone_azimuth_resolution,
                                                         cls.drop_azimuth_resolution,
                                                         cls.cell_width_resolution,
                                                         cls.cell_height_resolution,
                                                         cls.cell_required_area)

    def test_slide(self):
        self.assertEqual(self.slide1,
                         Slide(self.slide_properties_tiny))

    def test_slide_container(self):
        slide_1_locations = self.slides_container.get_envelope_location(self.drone_azimuth, self.drop_azimuth,
                                                                        PackageType.TINY)
        slide_2_locations = self.slides_container.get_envelope_location(self.drone_azimuth, self.drop_azimuth,
                                                                        PackageType.MEDIUM)

        self.assertEqual(self.slide1.envelope_location, slide_1_locations)
        self.assertEqual(self.slide2.envelope_location, slide_2_locations)
