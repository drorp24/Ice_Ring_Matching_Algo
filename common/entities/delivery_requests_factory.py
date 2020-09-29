from __future__ import annotations

from datetime import datetime
from typing import List

from common.entities.package import PackageType
from common.entities.package_factory import package_delivery_plan_factory
from common.entities.customer_delivery import CustomerDelivery
from common.entities.delivery_option import DeliveryOption
from common.entities.delivery_request import DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan
from time_window import TimeWindow

from delivery_request_conf import DeliveryRequestConf

#
# def create_delivery_request(num_of_delivery_options, num_of_customer_delivery, num_of_package_delivery_plans per Customer Delivery, Set of drop points) -> DeliveryRequest:
#     return DeliveryRequest()
from geometry import geo_factory
from geometry.geo2d import Point2D


def create_delivery_requests_from_file(file_path) -> List[DeliveryRequest]:
    delivery_requests_conf = DeliveryRequestConf.from_file(file_path)
    delivery_requests = [__create_delivery_request_from_dict(delivery_request_dict) for delivery_request_dict in
                         delivery_requests_conf['delivery_requests']]
    return delivery_requests


def __create_delivery_request_from_dict(delivery_request_dict) -> DeliveryRequest:
    start_time_dict = delivery_request_dict['time_window']['start_time']
    end_time_dict = delivery_request_dict['time_window']['end_time']
    return DeliveryRequest(
        delivery_options=[__create_delivery_option_from_dict(delivery_option_dict) for delivery_option_dict in
                          delivery_request_dict['delivery_options']],
        time_window=TimeWindow(datetime(start_time_dict['year'], start_time_dict['month'], start_time_dict['day'],
                                        start_time_dict['hour'], start_time_dict['minute'], start_time_dict['seconds']),
                               datetime(end_time_dict['year'], end_time_dict['month'], end_time_dict['day'],
                                        end_time_dict['hour'], end_time_dict['minute'], end_time_dict['seconds'])),
        priority=delivery_request_dict['priority'])


def __create_delivery_option_from_dict(delivery_option_dict) -> DeliveryOption:
    return DeliveryOption(
        customer_deliveries=[__create_customer_delivery_from_dict(customer_delivery_dict) for customer_delivery_dict in
                             delivery_option_dict['customer_deliveries']])


def __create_customer_delivery_from_dict(customer_delivery_dict) -> CustomerDelivery:
    # return CustomerDelivery([__create_package_delivery_plan_from_dict([package_delivery_plan_dict['package_delivery_plan'] for package_delivery_plan_dict in customer_delivery_dict])
    return CustomerDelivery(package_delivery_plans=[
        __create_package_delivery_plan_from_dict(customer_delivery_dict['package_delivery_plan'])])


def __create_package_delivery_plan_from_dict(package_delivery_plan_dict) -> PackageDeliveryPlan:
    return package_delivery_plan_factory(point=geo_factory.create_point_2d(package_delivery_plan_dict['drop_point_x'],
                                                       package_delivery_plan_dict['drop_point_y']),
                                         azimuth=package_delivery_plan_dict['azimuth'],
                                         elevation=package_delivery_plan_dict['elevation'],
                                         package=PackageType[package_delivery_plan_dict['package_type'].upper()])


delivery_requests = create_delivery_requests_from_file('..\..\DeliveryRequest.json')
a = 1
