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


class SupplierCategory(JsonableBaseEntity):

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
        return SupplierCategory(
            delivery_requests=[DeliveryRequest.dict_to_obj(dr_dict) for dr_dict in dict_input['delivery_requests']],
            drone_loading_docks=[DroneLoadingDock.dict_to_obj(dld_dict)
                                 for dld_dict in dict_input['drone_loading_docks']],
            zero_time=DateTimeExtension.from_dict(dict_input['zero_time']))

    def __eq__(self, other):
        return self.zero_time == other.zero_time and self.delivery_requests == other.delivery_requests and \
               self.drone_loading_docks == other.drone_loading_docks


