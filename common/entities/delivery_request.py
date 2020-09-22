from typing import List

from rafazonscale.common.entities.delivery_option import DeliveryOption


class DeliveryRequest:

    def __init__(self, delivery_options: List[DeliveryOption], since_time: int, until_time: int, priority: int):
        self._type = 'DeliveryRequest'
        self._delivery_options = delivery_options
        self._since_time = since_time
        self._until_time = until_time
        self._priority = priority

    @property
    def type(self) -> str:
        return self._type

    @property
    def delivery_options(self) -> str:
        return self._delivery_options

    @property
    def since_time(self) -> int:
        return self._since_time

    @property
    def until_time(self) -> int:
        return self._until_time

    @property
    def priority(self) -> int:
        return self._priority
