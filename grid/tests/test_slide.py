import unittest

from common.entities.package import PackageType
from common.math.angle import Angle, AngleUnit
from grid.slide import Slide
from grid.slides_factory import create_slide, generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicSlideTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.envelope_service = MockEnvelopeServices()
        cls.drone_azimuth = Angle(90, AngleUnit.DEGREE)
        cls.drop_azimuth = Angle(45, AngleUnit.DEGREE)
        cls.cell_resolution = 1
        cls.cell_ratio_required = 0.5
        cls.drone_azimuth_resolution = 4
        cls.drop_azimuth_resolution = 4

        cls.slide1 = create_slide(cls.envelope_service, PackageType.TINY, cls.drone_azimuth, cls.drop_azimuth,
                                  cls.cell_resolution, cls.cell_ratio_required)

        cls.slide2 = create_slide(cls.envelope_service, PackageType.MEDIUM, cls.drone_azimuth, cls.drop_azimuth,
                                  cls.cell_resolution, cls.cell_ratio_required)

        cls.package_types = [package_type for package_type in PackageType]
        cls.slides_container = generate_slides_container(cls.envelope_service,
                                                         cls.package_types,
                                                         cls.drone_azimuth_resolution,
                                                         cls.drop_azimuth_resolution,
                                                         cls.cell_resolution,
                                                         cls.cell_ratio_required)

    def test_slide(self):
        self.assertEqual(self.slide1,
                         Slide(self.envelope_service, PackageType.TINY, self.drone_azimuth, self.drop_azimuth,
                               self.cell_resolution, self.cell_ratio_required))

    def test_slide_container(self):
        slide_1_locations = self.slides_container.get_envelope_locations(self.drone_azimuth, self.drop_azimuth,
                                                                         PackageType.TINY)
        slide_2_locations = self.slides_container.get_envelope_locations(self.drone_azimuth, self.drop_azimuth,
                                                                         PackageType.MEDIUM)

        self.assertEqual(self.slide1.envelope_locations, slide_1_locations)
        self.assertEqual(self.slide2.envelope_locations, slide_2_locations)

