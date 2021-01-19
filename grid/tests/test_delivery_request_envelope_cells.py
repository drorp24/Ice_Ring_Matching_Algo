import unittest
from datetime import date, time
from uuid import UUID

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from grid.azimuth_options import AzimuthOptions
from grid.grid_cell import GridCell, EnvelopeGridCell
from grid.grid_cell_services import GridCellServices
from grid.delivery_request_envelope_cells import PotentialEnvelope, DeliveryRequestPotentialEnvelopes
from grid.grid_location import GridLocation, GridLocationServices
from grid.grid_service import GridService
from grid.slides_factory import generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicDeliveryRequestEnvelopeCellsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.envelope_service = MockEnvelopeServices()
        cls.cell_width_resolution = 1
        cls.cell_height_resolution = 2
        cls.cell_ratio_required = 0.5
        cls.drone_azimuth_resolution = 8
        cls.drop_azimuth_resolution = 8
        cls.package_types = [package_type for package_type in PackageType]
        cls.slides_container = generate_slides_container(MockEnvelopeServices(),
                                                         cls.package_types,
                                                         cls.drone_azimuth_resolution,
                                                         cls.drop_azimuth_resolution,
                                                         cls.cell_width_resolution,
                                                         cls.cell_height_resolution,
                                                         cls.cell_ratio_required)

        cls.pdp_1 = PackageDeliveryPlan(id=EntityID(UUID(int=42)),
                                        drop_point=create_point_2d(10, 20),
                                        azimuth=Angle(135, AngleUnit.DEGREE),
                                        pitch=Angle(90, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_2 = PackageDeliveryPlan(id=EntityID(UUID(int=43)),
                                        drop_point=create_point_2d(20, 30),
                                        azimuth=Angle(135, AngleUnit.DEGREE),
                                        pitch=Angle(45, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_3 = PackageDeliveryPlan(id=EntityID(UUID(int=44)),
                                        drop_point=create_point_2d(30, 40),
                                        azimuth=Angle(45, AngleUnit.DEGREE),
                                        pitch=Angle(45, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.do_1 = DeliveryOption([CustomerDelivery([cls.pdp_1, cls.pdp_2, cls.pdp_3])])

        cls.dr_1 = DeliveryRequest(delivery_options=[cls.do_1],
                                   time_window=TimeWindowExtension(
                                       DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                                       DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                                   priority=1)

        cls.delivery_requests_envelope_cells = DeliveryRequestPotentialEnvelopes(cls.slides_container, cls.dr_1)
        cls.delivery_requests_envelope_cells_dict_do_1 = cls.delivery_requests_envelope_cells.delivery_options_cells[0]

    def test_drone_azimuth(self):
        self.assertEqual(self.delivery_requests_envelope_cells_dict_do_1.keys(),
                         AzimuthOptions(self.slides_container.get_drone_azimuth_resolution).values)

    def test_envelope_cells(self):
        pdp_list = [self.pdp_1, self.pdp_2, self.pdp_3]
        for drone_azimuth in AzimuthOptions(self.slides_container.get_drone_azimuth_resolution).values:
            scale_to_grid_list = self._scale_to_grid_list(drone_azimuth, pdp_list)

            self._test_envelope_cells_average(drone_azimuth, scale_to_grid_list)

            self._test_envelope_cells_pdp_ids(drone_azimuth, scale_to_grid_list)

    def _test_envelope_cells_pdp_ids(self, drone_azimuth, scale_to_grid_list):
        empty_indices = GridLocationServices.get_not_empty_indices(scale_to_grid_list)
        package_delivery_plan_list = list(map([self.pdp_1, self.pdp_2, self.pdp_3].__getitem__, empty_indices))
        self.assertEqual(
            self.delivery_requests_envelope_cells_dict_do_1[
                drone_azimuth].package_delivery_plans_ids(),
            [package_delivery_plan.id for package_delivery_plan in package_delivery_plan_list])

    def _test_envelope_cells_average(self, drone_azimuth, scale_to_grid_list):
        expected_average_location = GridLocationServices.calc_average(scale_to_grid_list)
        self.assertEqual(self.delivery_requests_envelope_cells_dict_do_1[drone_azimuth].location,
                         expected_average_location)

    def _scale_to_grid_list(self, drone_azimuth, pdp_list):
        scale_to_grid_list = []
        for pdp in pdp_list:
            drop_point_grid_location = \
                GridService.get_grid_location(pdp.drop_point, self.slides_container.cell_width_resolution,
                                              self.slides_container.cell_height_resolution)
            drop_azimuth = GridCellServices.get_drop_azimuth(drone_azimuth, pdp.azimuth, pdp.pitch)
            envelope_location = self.slides_container.get_envelope_location(drone_azimuth,
                                                                            drop_azimuth,
                                                                            pdp.package_type)
            scale_to_grid_list.append(GridService.scale_to_grid(drop_point_grid_location, envelope_location))
        return scale_to_grid_list


class BasicDeliveryRequestEnvelopeCellsDictTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cell_1 = GridCell(location=GridLocation(10, 15))

        cls.pdp_1 = PackageDeliveryPlan(id=EntityID(UUID(int=42)),
                                        drop_point=create_point_2d(1, 2),
                                        azimuth=Angle(30, AngleUnit.DEGREE),
                                        pitch=Angle(80, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_2 = PackageDeliveryPlan(id=EntityID(UUID(int=43)),
                                        drop_point=create_point_2d(1, 3),
                                        azimuth=Angle(40, AngleUnit.DEGREE),
                                        pitch=Angle(90, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.envelope_cell_1 = EnvelopeGridCell(location=GridLocation(10, 15),
                                               drone_azimuth=Angle(45, AngleUnit.DEGREE),
                                               package_delivery_plans=[cls.pdp_1, cls.pdp_2])

        cls.envelope_cell_2 = EnvelopeGridCell(location=GridLocation(20, 15),
                                               drone_azimuth=Angle(90, AngleUnit.DEGREE),
                                               package_delivery_plans=[cls.pdp_1, cls.pdp_2])

        cls.delivery_request_envelope_cells = PotentialEnvelope(
            [cls.envelope_cell_1, cls.envelope_cell_2])

    def test_delivery_request_envelope_cells_dict(self):
        ec1_expected_grid_location = GridLocation(10, 15)
        ec1_expected_angle = Angle(45, AngleUnit.DEGREE)

        ec2_expected_grid_location = GridLocation(20, 15)
        ec2_expected_angle = Angle(90, AngleUnit.DEGREE)

        expected_pdp_1 = PackageDeliveryPlan(id=EntityID(UUID(int=42)),
                                             drop_point=create_point_2d(1, 2),
                                             azimuth=Angle(30, AngleUnit.DEGREE),
                                             pitch=Angle(80, AngleUnit.DEGREE),
                                             package_type=PackageType.TINY)

        expected_pdp_2 = PackageDeliveryPlan(id=EntityID(UUID(int=43)),
                                             drop_point=create_point_2d(1, 3),
                                             azimuth=Angle(40, AngleUnit.DEGREE),
                                             pitch=Angle(90, AngleUnit.DEGREE),
                                             package_type=PackageType.TINY)

        expected_pdp_list = [expected_pdp_1, expected_pdp_2]

        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].location, ec1_expected_grid_location)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].drone_azimuth, ec1_expected_angle)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].package_delivery_plans,
                         expected_pdp_list)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].package_delivery_plans_ids(),
                         [pdp.id for pdp in expected_pdp_list])

        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].location, ec2_expected_grid_location)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].drone_azimuth, ec2_expected_angle)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].package_delivery_plans,
                         expected_pdp_list)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].package_delivery_plans_ids(),
                         [pdp.id for pdp in expected_pdp_list])
