from datetime import date, time
from random import Random
from typing import List, Dict, Union

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.distribution_utils import get_updated_internal_amount, \
    validate_amount_input, extract_amount_in_range
from common.entities.base_entities.entity_distribution.drone_loading_dock_distribution import \
    DroneLoadingDockDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import DateTimeDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.temporal import DateTimeExtension
from common.entities.distribution.distribution import Distribution, Range


class Scenario(JsonableBaseEntity):

    def __init__(self, delivery_requests: List[DeliveryRequest], drone_loading_docks: List[DroneLoadingDock],
                 zero_time: DateTimeExtension):
        self._delivery_requests = delivery_requests
        self._drone_loading_docks = drone_loading_docks
        self._zero_time = zero_time

    @property
    def delivery_requests(self) -> List[DeliveryRequest]:
        return self._delivery_requests

    @property
    def drone_loading_docks(self) -> List[DroneLoadingDock]:
        return self._drone_loading_docks

    @property
    def zero_time(self) -> DateTimeExtension:
        return self._zero_time

    @classmethod
    def dict_to_obj(cls, dict_input):
        return Scenario(
            delivery_requests=[DeliveryRequest.dict_to_obj(dr_dict) for dr_dict in dict_input['delivery_requests']],
            drone_loading_docks=[DroneLoadingDock.dict_to_obj(dld_dict)
                                 for dld_dict in dict_input['drone_loading_docks']],
            zero_time=DateTimeExtension.from_dict(dict_input['zero_time']))


DEFAULT_DATE_TIME_MORNING = [DateTimeExtension(dt_date=date(2021, 1, 1), dt_time=time(6, 0, 0))]


class ScenarioDistribution(Distribution):

    def __init__(self, delivery_requests_distribution: DeliveryRequestDistribution = DeliveryRequestDistribution(),
                 drone_loading_docks_distribution: DroneLoadingDockDistribution = DroneLoadingDockDistribution(),
                 zero_time_distribution: DateTimeDistribution = DateTimeDistribution(DEFAULT_DATE_TIME_MORNING)):
        self.delivery_requests_distribution = delivery_requests_distribution
        self.drone_loading_docks_distribution = drone_loading_docks_distribution
        self.zero_time_distribution = zero_time_distribution

    def choose_rand(self, random: Random, amount: Dict[type, Union[int, Range]] = {}) -> Scenario:
        validate_amount_input(self, amount)
        internal_amount = get_updated_internal_amount(ScenarioDistribution, amount)
        sc_amount = extract_amount_in_range(internal_amount.pop(Scenario), random)
        dld_amount = extract_amount_in_range(internal_amount.pop(DroneLoadingDock), random)
        zero_time = self.zero_time_distribution.choose_rand(random=random, amount=1)
        return [Scenario(self.delivery_requests_distribution.choose_rand(random=random, amount=internal_amount),
                        self.drone_loading_docks_distribution.choose_rand(random=random, amount=dld_amount),
                        zero_time[0]) for _ in range(sc_amount)]

    @classmethod
    def distribution_class(cls) -> type:
        return Scenario

    @staticmethod
    def get_all_internal_types():
        return [Scenario, DeliveryRequest, DeliveryOption, CustomerDelivery, PackageDeliveryPlan, DroneLoadingDock]
