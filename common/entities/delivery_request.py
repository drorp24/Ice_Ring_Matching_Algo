from rafazonscale.common.entities.delivery_option import DeliveryOption
from time_window import TimeWindow

class DeliveryRequest:

    def __init__(self, delivery_options: [DeliveryOption], time_window :TimeWindow, priority: int):
        if not isinstance(delivery_options, list):
            raise TypeError("delivery_options must be a list")

        self._delivery_options = delivery_options if delivery_options is not None else []
        self.time_window = time_window
        self._priority = priority

    @property
    def delivery_options(self) -> [DeliveryOption]:
        return self._delivery_options

    @property
    def time_window(self) -> TimeWindow:
        return self._time_window

    @property
    def priority(self) -> int:
        return self._priority
