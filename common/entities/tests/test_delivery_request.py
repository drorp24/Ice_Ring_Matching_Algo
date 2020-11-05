import unittest
from datetime import datetime
from pathlib import Path

from time_window import TimeWindow

from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d
from input.delivery_requests_json_converter import create_delivery_requests_from_file


class BasicDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr_from_file = create_delivery_requests_from_file(Path('DeliveryRequestTest.json'))
        cls.dr_from_scratch = DeliveryRequest(
            delivery_options=[
                DeliveryOption([
                    CustomerDelivery([
                        PackageDeliveryPlan(drop_point=create_point_2d(5.0, 7.0),
                                            azimuth=Angle(45, AngleUnit.DEGREE),
                                            pitch=Angle(30, AngleUnit.DEGREE),
                                            package_type=PackageType.MEDIUM)]),
                    CustomerDelivery([
                        PackageDeliveryPlan(drop_point=create_point_2d(5.0, 7.0),
                                            azimuth=Angle(55, AngleUnit.DEGREE),
                                            pitch=Angle(40, AngleUnit.DEGREE),
                                            package_type=PackageType.LARGE)])]),
                DeliveryOption([
                    CustomerDelivery([
                        PackageDeliveryPlan(drop_point=create_point_2d(5.0, 7.0),
                                            azimuth=Angle(45, AngleUnit.DEGREE),
                                            pitch=Angle(30, AngleUnit.DEGREE),
                                            package_type=PackageType.MEDIUM)]),
                    CustomerDelivery([
                        PackageDeliveryPlan(drop_point=create_point_2d(5.0, 7.0),
                                            azimuth=Angle(55, AngleUnit.DEGREE),
                                            pitch=Angle(40, AngleUnit.DEGREE),
                                            package_type=PackageType.LARGE)])])],
            time_window=TimeWindow(
                datetime(2020, 1, 1,
                         6, 6, 6),
                datetime(2020, 1, 1,
                         8, 6, 6)),
            priority=0)

    def test_customer_delivery_length(self):
        self.assertEqual(len(self.dr_from_file[0].delivery_options[0].customer_deliveries), 1)

    def test_2_customer_deliveries_equal(self):
        self.assertEqual(self.dr_from_scratch.delivery_options[0].customer_deliveries[0],
                         self.dr_from_scratch.delivery_options[1].customer_deliveries[0])

    def test_2_customer_deliveries_not_equal(self):
        self.assertNotEqual(self.dr_from_scratch.delivery_options[0].customer_deliveries[0],
                            self.dr_from_scratch.delivery_options[0].customer_deliveries[1])

    def test_delivery_option_length(self):
        self.assertEqual(len(self.dr_from_file[0].delivery_options), 2)

    def test_delivery_request_length(self):
        self.assertEqual(len(self.dr_from_file), 3)

    def test_delivery_request_time_window(self):
        self.assertFalse(self.dr_from_file[0].time_window.since > self.dr_from_file[0].time_window.until)

    def test_delivery_request_priority(self):
        self.assertEqual(self.dr_from_file[0].priority, 10)
