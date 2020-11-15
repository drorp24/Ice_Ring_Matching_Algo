from attr import dataclass
from time_window import TimeWindow
from common.entities.delivery_option import DeliveryOption
from common.entities.keys import DeliveryRequestId
import uuid


class DeliveryRequest:

    def __init__(self, delivery_options: [DeliveryOption], time_window :TimeWindow, priority: int):
        self._delivery_options = delivery_options if delivery_options is not None else []
        self._time_window = time_window
        self._priority = priority
        self._id = uuid.uuid1()     # todo get id as an input

    def __eq__(self, other):
        return (self.delivery_options == other.delivery_options) and \
               (self.time_window == other.time_window) and \
               (self.priority == other.priority)

    @property
    def delivery_options(self) -> [DeliveryOption]:
        return self._delivery_options

    @property
    def time_window(self) -> TimeWindow:
        return self._time_window

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def id(self) -> uuid:
        return self._id
