import unittest
from uuid import UUID

from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlanList, PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from grid.cell import Cell, EnvelopeCell, CellServices
from grid.grid_location import GridLocation


class BasicCellTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cell_1 = Cell(location=GridLocation(10, 15))

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

        cls.envelope_cell_1 = EnvelopeCell(location=GridLocation(10, 15),
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

        expected_pdp_list = PackageDeliveryPlanList([expected_pdp_1,expected_pdp_2])

        self.assertEqual(self.envelope_cell_1.location, expected_grid_location)
        self.assertEqual(self.envelope_cell_1.drone_azimuth, expected_angle)
        self.assertEqual(self.envelope_cell_1.package_delivery_plans,expected_pdp_list)
        self.assertEqual(self.envelope_cell_1.package_delivery_plans.ids, expected_pdp_list.ids)

class BasicCellServiceTestCase(unittest.TestCase):

    def test_cell_service_commutative(self):
        cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        cell2 = EnvelopeCell(GridLocation(2, 3), Angle(15, AngleUnit.DEGREE))
        dist12 = CellServices.get_distance(cell1, cell2)
        dist21 = CellServices.get_distance(cell2, cell1)
        self.assertEqual(dist12, dist21)

    def test_cell_service_angle(self):
        pass
        # cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        # cell2 = EnvelopeCell(GridLocation(0, 0), Angle(15, AngleUnit.DEGREE))
        # cell3 = EnvelopeCell(GridLocation(0, 0), Angle(30, AngleUnit.DEGREE))
        # dist12 = CellServices.get_distance(cell1, cell2)
        # dist13 = CellServices.get_distance(cell1, cell3)
        # dist23 = CellServices.get_distance(cell2, cell3)
        #
        # self.assertEqual(dist12, dist23)
        # self.assertGreater(dist13, dist12)

    def test_cell_service_grid_location(self):
        pass
        # cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        # cell2 = EnvelopeCell(GridLocation(1, 1), Angle(0, AngleUnit.DEGREE))
        # cell3 = EnvelopeCell(GridLocation(2, 2), Angle(0, AngleUnit.DEGREE))
        # dist12 = CellServices.get_distance(cell1, cell2)
        # dist13 = CellServices.get_distance(cell1, cell3)
        # dist23 = CellServices.get_distance(cell2, cell3)
        #
        # self.assertEqual(dist12, dist23)
        # self.assertGreater(dist13, dist12)

    def test_cell_service_angle_delta_cost(self):
        pass
        #cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        # cell2 = EnvelopeCell(GridLocation(1, 1), Angle(0, AngleUnit.DEGREE))
        # cell3 = EnvelopeCell(GridLocation(2, 2), Angle(0, AngleUnit.DEGREE))
        # dist12 = CellServices.get_distance(cell1, cell2)
        # dist13 = CellServices.get_distance(cell1, cell3)
        # dist23 = CellServices.get_distance(cell2, cell3)
        #
        # self.assertEqual(dist12, dist23)
        # self.assertGreater(dist13, dist12)