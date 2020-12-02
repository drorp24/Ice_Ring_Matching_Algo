from datetime import date, time
from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.delivery_request import DeliveryRequest, DeliveryRequestDistribution
from common.entities.disribution.distribution import Distribution
from common.entities.drone_loading_dock import DroneLoadingDock, DroneLoadingDockDistribution
from common.entities.temporal import DateTimeExtension, DateTimeDistribution


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

    def choose_rand(self, random: Random, amount: int, dock_amount: int = 1) -> Scenario:
        zero_time = self.zero_time_distribution.choose_rand(random=random, amount=1)
        return Scenario(self.delivery_requests_distribution.choose_rand(random, amount),
                        self.drone_loading_docks_distribution.choose_rand(random, dock_amount),
                        zero_time[0])
