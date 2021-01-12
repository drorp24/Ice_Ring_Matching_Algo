import unittest
from datetime import date, time
from random import Random
from typing import List
from uuid import UUID

import numpy as np

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.base_entities.entity_id import EntityID
from common.entities.generator.delivery_request_generator import DeliveryRequestDatasetGenerator, DeliveryRequestDatasetStructure
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.temporal import TimeWindowExtension, DateTimeExtension
from common.math.angle import Angle, AngleUnit
from geometry.distribution.geo_distribution import UniformPointInBboxDistribution
from geometry.geo_factory import create_point_2d
from grid.grid import DeliveryRequestsGrid
from grid.slides_container import SlidesContainer
from grid.slides_factory import generate_slides_container
from services.mock_envelope_services import MockEnvelopeServices


class BasicGridTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slides_container = generate_slide_container()

        cls.dr_data_set_1 = create_distributed_dr_data_set()
        cls.delivery_requests_grid_1 = DeliveryRequestsGrid(cls.slides_container, cls.dr_data_set_1)

        cls.dr_data_set_2 = create_no_zero_dist_dr_data_set()
        cls.delivery_requests_grid_2 = DeliveryRequestsGrid(cls.slides_container, cls.dr_data_set_2)

        cls.dr_data_set_3 = create_inf_dist_dr_data_set()
        cls.delivery_requests_grid_3 = DeliveryRequestsGrid(cls.slides_container, cls.dr_data_set_3)

    def test_delivery_requests(self):
        delivery_requests = self.delivery_requests_grid_1.delivery_requests_envelope_cells.keys()
        self.assertTrue(set(self.dr_data_set_1).issubset(delivery_requests))

    def test_zero_distance(self):
        expected_distance = 0

        for dr in self.dr_data_set_1:
            self.assertEqual(self.delivery_requests_grid_1.get_distance_between_delivery_options(dr, dr, 0, 0), expected_distance)

    def test_non_zero_distance(self):
        expected_distance = 22.36

        self.assertEqual(
            round(self.delivery_requests_grid_2.get_distance_between_delivery_options(self.dr_data_set_2[0],
                                                                                      self.dr_data_set_2[1], 0, 0), 2),
            expected_distance)

    def test_inf_distance(self):
        expected_distance = np.inf

        self.assertEqual(
            self.delivery_requests_grid_3.get_distance_between_delivery_options(self.dr_data_set_3[0],
                                                                                self.dr_data_set_3[1], 0, 0),
            expected_distance)


def generate_slide_container() -> SlidesContainer:
    cell_width_resolution = 1
    cell_height_resolution = 2
    cell_ratio_required = 0.5
    drone_azimuth_resolution = 8
    drop_azimuth_resolution = 8
    package_types = [package_type for package_type in PackageType]
    return generate_slides_container(MockEnvelopeServices(),
                                     package_types,
                                     drone_azimuth_resolution,
                                     drop_azimuth_resolution,
                                     cell_width_resolution,
                                     cell_height_resolution,
                                     cell_ratio_required)


def create_distributed_dr_data_set():
    dr_struct = DeliveryRequestDatasetStructure(num_of_delivery_requests=10,
                                                num_of_delivery_options_per_delivery_request=1,
                                                num_of_customer_deliveries_per_delivery_option=2,
                                                num_of_package_delivery_plan_per_customer_delivery=3,
                                                delivery_request_distribution=(_create_dr_distribution()))
    return DeliveryRequestDatasetGenerator.generate(dr_struct, random=Random(42))


def _create_dr_distribution():
    return build_delivery_request_distribution(
        relative_pdp_location_distribution=UniformPointInBboxDistribution(min_x=10, max_x=1200, min_y=10, max_y=1150))


def create_no_zero_dist_dr_data_set() -> List[DeliveryRequest]:
    pdp_1 = PackageDeliveryPlan(id=EntityID(UUID(int=42)),
                                drop_point=create_point_2d(10, 20),
                                azimuth=Angle(135, AngleUnit.DEGREE),
                                pitch=Angle(90, AngleUnit.DEGREE),
                                package_type=PackageType.TINY)

    do_1 = DeliveryOption([CustomerDelivery([pdp_1])])
    dr_1 = DeliveryRequest(delivery_options=[do_1],
                           time_window=TimeWindowExtension(
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                           priority=1)

    pdp_2 = PackageDeliveryPlan(id=EntityID(UUID(int=44)),
                                drop_point=create_point_2d(30, 40),
                                azimuth=Angle(45, AngleUnit.DEGREE),
                                pitch=Angle(45, AngleUnit.DEGREE),
                                package_type=PackageType.TINY)
    do_2 = DeliveryOption([CustomerDelivery([pdp_2])])
    dr_2 = DeliveryRequest(delivery_options=[do_2],
                           time_window=TimeWindowExtension(
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                           priority=1)
    return [dr_1, dr_2]


def create_inf_dist_dr_data_set() -> List[DeliveryRequest]:
    pdp_1 = PackageDeliveryPlan(id=EntityID(UUID(int=42)),
                                drop_point=create_point_2d(10, 20),
                                azimuth=Angle(270, AngleUnit.DEGREE),
                                pitch=Angle(270, AngleUnit.DEGREE),
                                package_type=PackageType.TINY)

    do_1 = DeliveryOption([CustomerDelivery([pdp_1])])
    dr_1 = DeliveryRequest(delivery_options=[do_1],
                           time_window=TimeWindowExtension(
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                           priority=1)

    pdp_2 = PackageDeliveryPlan(id=EntityID(UUID(int=44)),
                                drop_point=create_point_2d(30, 40),
                                azimuth=Angle(45, AngleUnit.DEGREE),
                                pitch=Angle(45, AngleUnit.DEGREE),
                                package_type=PackageType.TINY)
    do_2 = DeliveryOption([CustomerDelivery([pdp_2])])
    dr_2 = DeliveryRequest(delivery_options=[do_2],
                           time_window=TimeWindowExtension(
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0)),
                               DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))),
                           priority=1)
    return [dr_1, dr_2]
