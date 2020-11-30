from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.delivery_request import DeliveryRequest
from common.entities.drone_loading_dock import DroneLoadingDock
from common.entities.temporal import DateTimeExtension


class Scenario(JsonableBaseEntity):

    def __init__(self, delivery_requests: List[DeliveryRequest], drone_loading_docks: List[DroneLoadingDock],
                 zero_time: DateTimeExtension):
        self.delivery_requests = delivery_requests
        self.drone_loading_docks = drone_loading_docks
        self.zero_time = zero_time

    @classmethod
    def dict_to_obj(cls, dict_input):
        return Scenario(
            delivery_requests=[DeliveryRequest.dict_to_obj(dr_dict) for dr_dict in dict_input['delivery_requests']],
            drone_loading_docks=[DroneLoadingDock.dict_to_obj(dld_dict)
                                 for dld_dict in dict_input['drone_delivery_docks']],
            zero_time=DateTimeExtension.to_dict(dict_input['zero_time']))
