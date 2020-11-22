import unittest
from datetime import date, time
from uuid import UUID

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlanList, PackageDeliveryPlan
from common.entities.temporal import TimeWindowExtension, DateTimeExtension
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from grid.azimuth_options import AzimuthOptions
from grid.cell import Cell, EnvelopeCell
from grid.cell_services import CellServices
from grid.delivery_request_envelope_cells import DeliveryRequestEnvelopeCellsDict, DeliveryRequestEnvelopeCells
from grid.grid_location import GridLocation, GridLocationServices
from grid.grid_service import GridService
from grid.slides_factory import generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicDeliveryRequestEnvelopeCellsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.envelope_service = MockEnvelopeServices()
        cls.cell_resolution = 1
        cls.cell_ratio_required = 0.5
        cls.drone_azimuth_resolution = 8
        cls.drop_azimuth_resolution = 8
        cls.package_types = [package_type for package_type in PackageType]
        cls.slides_container = generate_slides_container(MockEnvelopeServices(),
                                                         cls.package_types,
                                                         cls.drone_azimuth_resolution,
                                                         cls.drop_azimuth_resolution,
                                                         cls.cell_resolution,
                                                         cls.cell_ratio_required)
        print(cls.slides_container)

        cls.pdp_1 = PackageDeliveryPlan(id=UUID(int=42),
                                        drop_point=create_point_2d(1, 2),
                                        azimuth=Angle(135, AngleUnit.DEGREE),
                                        pitch=Angle(90, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.pdp_2 = PackageDeliveryPlan(id=UUID(int=43),
                                        drop_point=create_point_2d(1, 3),
                                        azimuth=Angle(135, AngleUnit.DEGREE),
                                        pitch=Angle(45, AngleUnit.DEGREE),
                                        package_type=PackageType.TINY)

        cls.do_1 = DeliveryOption([CustomerDelivery([cls.pdp_1, cls.pdp_2])])

        cls.dr_1 = DeliveryRequest(delivery_options=[cls.do_1],
                                   time_window=TimeWindowExtension(
                                       DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                                       DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                                   priority=1)

        cls.delivery_requests_envelope_cells = DeliveryRequestEnvelopeCells(cls.slides_container, cls.dr_1)
        cls.delivery_requests_envelope_cells_dict_do_1 = cls.delivery_requests_envelope_cells.cells[0]

    def test_drone_azimuth(self):
        self.assertEqual(self.delivery_requests_envelope_cells_dict_do_1.keys(),
                         AzimuthOptions(self.slides_container.get_drone_azimuth_resolution).values)

    def test_envelope_cells(self):
        pass
        # drone_azimuth = Angle(45.0, AngleUnit.DEGREE)
        # pdp_1_drop_azimuth = CellServices.get_drop_azimuth(drone_azimuth, self.pdp_1.azimuth,
        #                                                    self.pdp_1.pitch)
        #
        # pdp_2_drop_azimuth = CellServices.get_drop_azimuth(drone_azimuth, self.pdp_2.azimuth,
        #                                                    self.pdp_2.pitch)
        #
        # pdp_1_envelope_location = self.slides_container.get_envelope_location(drone_azimuth,
        #                                                                       pdp_1_drop_azimuth,
        #                                                                       self.pdp_1.package_type)
        #
        # pdp_2_envelope_location = self.slides_container.get_envelope_location(drone_azimuth,
        #                                                                       pdp_2_drop_azimuth,
        #                                                                       self.pdp_2.package_type)
        #
        # pdp_1_drop_point_grid_location = GridService.get_grid_location(self.pdp_1.drop_point,
        #                                                                self.slides_container.get_drone_azimuth_resolution)
        #
        # pdp_2_drop_point_grid_location = GridService.get_grid_location(self.pdp_2.drop_point,
        #                                                                self.slides_container.get_drone_azimuth_resolution)
        #
        # pdp_1_scale_to_grid = GridService.scale_to_grid(pdp_1_drop_point_grid_location, pdp_1_envelope_location)
        # pdp_2_scale_to_grid = GridService.scale_to_grid(pdp_2_drop_point_grid_location, pdp_2_envelope_location)
        #
        # expected_average_location = GridLocationServices.calc_average([])

        #     self.assertEqual(self.delivery_requests_envelope_cells_dict_do_1[Angle(0, AngleUnit.DEGREE)].location,
        #                      expected_average_location)
        #     # for ec in self.delivery_requests_envelope_cells_dict_do_1.values():
        #     #     self.assertEqual(ec.location,
        #     #                      expected_average_location)


class BasicDeliveryRequestEnvelopeCellsDictTestCase(unittest.TestCase):

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

        cls.envelope_cell_2 = EnvelopeCell(location=GridLocation(20, 15),
                                           drone_azimuth=Angle(90, AngleUnit.DEGREE),
                                           package_delivery_plans=PackageDeliveryPlanList([cls.pdp_1, cls.pdp_2]))

        cls.delivery_request_envelope_cells = DeliveryRequestEnvelopeCellsDict(
            [cls.envelope_cell_1, cls.envelope_cell_2])

    def test_delivery_request_envelope_cells_dict(self):
        ec1_expected_grid_location = GridLocation(10, 15)
        ec1_expected_angle = Angle(45, AngleUnit.DEGREE)

        ec2_expected_grid_location = GridLocation(20, 15)
        ec2_expected_angle = Angle(90, AngleUnit.DEGREE)

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

        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].location, ec1_expected_grid_location)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].drone_azimuth, ec1_expected_angle)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].package_delivery_plans,
                         expected_pdp_list)
        self.assertEqual(self.delivery_request_envelope_cells[ec1_expected_angle].package_delivery_plans.ids,
                         expected_pdp_list.ids)

        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].location, ec2_expected_grid_location)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].drone_azimuth, ec2_expected_angle)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].package_delivery_plans,
                         expected_pdp_list)
        self.assertEqual(self.delivery_request_envelope_cells[ec2_expected_angle].package_delivery_plans.ids,
                         expected_pdp_list.ids)
