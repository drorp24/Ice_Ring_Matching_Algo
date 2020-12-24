import unittest
from uuid import UUID

from optional import Optional

from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from grid.grid_cell import EnvelopeGridCell
from grid.grid_cell_services import GridCellServices
from grid.grid_location import GridLocation


class BasicCellServiceTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdp_1 = PackageDeliveryPlan(id=UUID(int=42),
                                        drop_point=create_point_2d(1, 2),
                                        azimuth=Angle(30, AngleUnit.DEGREE),
                                        pitch=Angle(80, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_2 = PackageDeliveryPlan(id=UUID(int=42),
                                        drop_point=create_point_2d(1, 2),
                                        azimuth=Angle(30, AngleUnit.DEGREE),
                                        pitch=Angle(90, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

    def test_cell_service_angle(self):
        cell1 = EnvelopeGridCell(Optional.of(GridLocation(0, 0)), Angle(0, AngleUnit.DEGREE), [])
        cell2 = EnvelopeGridCell(Optional.of(GridLocation(0, 0)), Angle(15, AngleUnit.DEGREE), [])
        cell3 = EnvelopeGridCell(Optional.of(GridLocation(0, 0)), Angle(30, AngleUnit.DEGREE), [])
        dist12 = GridCellServices.calc_distance(cell1, cell2)
        dist13 = GridCellServices.calc_distance(cell1, cell3)
        dist23 = GridCellServices.calc_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)

    def test_cell_service_grid_location(self):
        cell1 = EnvelopeGridCell(Optional.of(GridLocation(0, 0)), Angle(0, AngleUnit.DEGREE), [])
        cell2 = EnvelopeGridCell(Optional.of(GridLocation(1, 1)), Angle(0, AngleUnit.DEGREE), [])
        cell3 = EnvelopeGridCell(Optional.of(GridLocation(2, 2)), Angle(0, AngleUnit.DEGREE), [])
        dist12 = GridCellServices.calc_distance(cell1, cell2)
        dist13 = GridCellServices.calc_distance(cell1, cell3)
        dist23 = GridCellServices.calc_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)

    def test_cell_service_angle_delta_cost(self):
        cell1 = EnvelopeGridCell(Optional.of(GridLocation(0, 0)), Angle(0, AngleUnit.DEGREE), [])
        cell2 = EnvelopeGridCell(Optional.of(GridLocation(1, 1)), Angle(0, AngleUnit.DEGREE), [])
        cell3 = EnvelopeGridCell(Optional.of(GridLocation(2, 2)), Angle(0, AngleUnit.DEGREE), [])
        dist12 = GridCellServices.calc_distance(cell1, cell2)
        dist13 = GridCellServices.calc_distance(cell1, cell3)
        dist23 = GridCellServices.calc_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)

    def test_get_drop_azimuth(self):
        expected_drone_azimuth = Angle(50, AngleUnit.DEGREE)

        expected_drop_azimuth_1 = GridCellServices.get_drop_azimuth(expected_drone_azimuth, self.pdp_1.azimuth,
                                                                    self.pdp_1.pitch)
        self.assertEqual(expected_drop_azimuth_1,
                         self.pdp_1.azimuth)

        expected_drop_azimuth_2 = GridCellServices.get_drop_azimuth(expected_drone_azimuth, self.pdp_2.azimuth,
                                                                    self.pdp_2.pitch)
        self.assertEqual(expected_drop_azimuth_2,
                         expected_drone_azimuth)
