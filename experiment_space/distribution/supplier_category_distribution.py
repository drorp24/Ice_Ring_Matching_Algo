from datetime import date, time
from random import Random
from typing import Dict, Union

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.distribution_utils import validate_amount_input, \
    get_updated_internal_amount, extract_amount_in_range
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import DateTimeDistribution
from common.entities.base_entities.entity_distribution.zone_delivery_request_distribution import \
    ZoneDeliveryRequestDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.temporal import DateTimeExtension
from common.entities.distribution.distribution import HierarchialDistribution, Range
from experiment_space.supplier_category import SupplierCategory

DEFAULT_DATE_TIME_MORNING = [DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))]


class SupplierCategoryDistribution(HierarchialDistribution):

    def __init__(self, delivery_requests_distribution: DeliveryRequestDistribution = DeliveryRequestDistribution(),
                 drone_loading_docks_distribution: DroneLoadingDockDistribution = DroneLoadingDockDistribution(),
                 zero_time_distribution: DateTimeDistribution = DateTimeDistribution(DEFAULT_DATE_TIME_MORNING)):
        self.delivery_requests_distribution = delivery_requests_distribution
        self.drone_loading_docks_distribution = drone_loading_docks_distribution
        self.zero_time_distribution = zero_time_distribution

    def choose_rand(self, random: Random, amount: Dict[type, Union[int, Range]] = {}) -> [SupplierCategory]:
        validate_amount_input(self, amount)
        internal_amount = get_updated_internal_amount(SupplierCategoryDistribution, amount)
        sc_amount = extract_amount_in_range(internal_amount.pop(SupplierCategory), random)
        dld_amount = extract_amount_in_range(internal_amount.pop(DroneLoadingDock), random)
        zero_time = self.zero_time_distribution.choose_rand(random=random, amount=sc_amount)
        zones = self.delivery_requests_distribution.zones if isinstance(self.delivery_requests_distribution,
                                                                        ZoneDeliveryRequestDistribution) else []
        return [SupplierCategory(self.delivery_requests_distribution.choose_rand(random=random, amount=internal_amount),
                                 self.drone_loading_docks_distribution.choose_rand(random=random, amount=dld_amount),
                                 zt, zones=zones) for zt in zero_time]

    @classmethod
    def distribution_class(cls) -> type:
        return SupplierCategory

    @staticmethod
    def get_all_internal_types():
        return [SupplierCategory, DeliveryRequest, DeliveryOption, CustomerDelivery, PackageDeliveryPlan,
                DroneLoadingDock]
