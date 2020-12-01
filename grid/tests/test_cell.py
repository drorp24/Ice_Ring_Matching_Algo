import unittest
from uuid import UUID

from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlanList, PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from grid.grid_cell import GridCell, EnvelopeGridCell
from grid.grid_location import GridLocation


class BasicCellTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cell_1 = GridCell(location=GridLocation(10, 15))

        cls.pdp_1 = PackageDeliveryPlan(id=UUID(int=42),
                                        drop_point=create_point_2d(1, 2),
                                        azimuth=Angle(30, AngleUnit.DEGREE),
                                        pitch=Angle(80, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_2 = PackageDeliveryPlan(id=UUID(int=43),
                                        drop_point=create_point_2d(1, 3),
                                        azimuth=Angle(40, AngleUnit.DEGREE),
                                        pitch=Angle(90, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.envelope_cell_1 = EnvelopeGridCell(location=GridLocation(10, 15),
                                               drone_azimuth=Angle(45, AngleUnit.DEGREE),
                                               package_delivery_plans=PackageDeliveryPlanList([cls.pdp_1, cls.pdp_2]))

    def test_cell(self):
        expected_grid_location = GridLocation(10, 15)
        self.assertEqual(self.cell_1.location, expected_grid_location)

    def test_envelope_cell(self):
        expected_grid_location = GridLocation(10, 15)
        expected_angle = Angle(45, AngleUnit.DEGREE)
        expected_pdp_1 = PackageDeliveryPlan(id=UUID(int=42),
                                             drop_point=create_point_2d(1, 2),
                                             azimuth=Angle(30, AngleUnit.DEGREE),
                                             pitch=Angle(80, AngleUnit.DEGREE),
                                             package_type=PackageType.TINY)

        expected_pdp_2 = PackageDeliveryPlan(id=UUID(int=43),
                                             drop_point=create_point_2d(1, 3),
                                             azimuth=Angle(40, AngleUnit.DEGREE),
                                             pitch=Angle(90, AngleUnit.DEGREE),
                                             package_type=PackageType.TINY)

        expected_pdp_list = PackageDeliveryPlanList([expected_pdp_1, expected_pdp_2])

        self.assertEqual(self.envelope_cell_1.location, expected_grid_location)
        self.assertEqual(self.envelope_cell_1.drone_azimuth, expected_angle)
        self.assertEqual(self.envelope_cell_1.package_delivery_plans, expected_pdp_list)
        self.assertEqual(self.envelope_cell_1.package_delivery_plans.ids, expected_pdp_list.ids)
