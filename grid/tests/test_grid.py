import unittest
from random import Random

from optional import Optional

from common.entities.delivery_request import generate_dr_distribution
from common.entities.delivery_request_generator import DeliveryRequestDatasetGenerator, DeliveryRequestDatasetStructure
from common.entities.package import PackageType
from geometry.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d, create_polygon_2d
from grid.grid import DeliveryRequestsGrid
from grid.grid_location import GridLocation, GridLocationServices
from grid.grid_service import GridService
from grid.slides_container import SlidesContainer
from grid.slides_factory import generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicGridTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dr_dataset_1 = create_local_data_in_region_1()
        cls.dr_dataset_2 = create_local_data_in_region_2()

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

        cls.delivery_requests_grid_1 = DeliveryRequestsGrid(cls.slides_container, cls.dr_dataset_1)
        cls.delivery_requests_grid_2 = DeliveryRequestsGrid(cls.slides_container, cls.dr_dataset_2)

    def test_delivery_requests(self):
        delivery_requests = self.delivery_requests_grid.delivery_requests_envelope_cells.keys()
        self.assertTrue(set(delivery_requests.issubset(self.dr_dataset)))

    def test_zero_distance(self):
        self.assertEqual(self.delivery_requests_grid_2.get_distance(self.dr_dataset_2[0], self.dr_dataset_2[1], 0, 0),
                         0)

    def test_non_zero_distance(self):
        self.assertGreater(self.delivery_requests_grid_1.get_distance(self.dr_dataset_1[0], self.dr_dataset_1[1], 0, 0),
                           0)


class BasicGridLocationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.row = 10
        cls.column = 15

        cls.grid_location_1 = GridLocation(10, 15)
        cls.grid_location_2 = GridLocation(20, 10)
        cls.grid_location_3 = GridLocation(60, 5)

        cls.grid_location_avg = GridLocation(30, 10)

    def test_grid_location(self):
        self.assertEqual(self.row, self.grid_location_1.row)
        self.assertEqual(self.column, self.grid_location_1.column)

    def test_grid_location_calc_average(self):
        average_grid_location = GridLocationServices.calc_average(
            [self.grid_location_1, self.grid_location_2, self.grid_location_3])

        self.assertEqual(self.grid_location_avg, average_grid_location)


class BasicGridServiceTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(21.0, 21.0)
        cls.grid_location_1 = GridLocation(10, 10)

        cls.p2 = create_point_2d(0.0, 0.0)
        cls.p3 = create_point_2d(0.0, 40.0)
        cls.p4 = create_point_2d(40.0, 40.0)
        cls.p5 = create_point_2d(40.0, 0.0)
        cls.poly1 = create_polygon_2d([cls.p2, cls.p3, cls.p4, cls.p5])

        cls.envelope_grid_location_1 = GridLocation(2, 2)
        cls.scale_to_grid_location_1 = GridService.scale_to_grid(cls.grid_location_1, cls.envelope_grid_location_1)
        cls.scale_to_grid_location_2 = GridService.scale_to_grid(cls.grid_location_1, Optional.empty())

    def test_get_grid_location(self):
        grid_location = GridService.get_grid_location(self.p1, 2)
        self.assertEqual(self.grid_location_1, grid_location)

    def test_get_polygon_centroid_grid_location(self):
        grid_location = GridService.get_polygon_centroid_grid_location(self.poly1, 2)
        self.assertEqual(self.grid_location_1, grid_location)

    def test_scale_to_grid(self):
        expected_scale_to_grid_location = GridLocation(12, 12)
        self.assertEqual(expected_scale_to_grid_location, self.scale_to_grid_location_1)
        self.assertEqual(Optional.empty(), self.scale_to_grid_location_2)


def create_local_data_in_region_1():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                num_of_delivery_options_per_delivery_request=1,
                                                num_of_customer_deliveries_per_delivery_option=2,
                                                num_of_package_delivery_plan_per_customer_delivery=3,
                                                delivery_request_distribution=(_create_region_1_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def create_local_data_in_region_2():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=2,
                                                num_of_delivery_options_per_delivery_request=1,
                                                num_of_customer_deliveries_per_delivery_option=1,
                                                num_of_package_delivery_plan_per_customer_delivery=1,
                                                delivery_request_distribution=(_create_region_2_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def _create_region_1_dr_distribution():
    return generate_dr_distribution(
        drop_point_distribution=UniformPointInBboxDistribution(min_x=10, max_x=1200, min_y=10, max_y=1150))


def _create_region_2_dr_distribution():
    return generate_dr_distribution(
        drop_point_distribution=UniformPointInBboxDistribution(min_x=1100, max_x=1100, min_y=1150, max_y=1150))
