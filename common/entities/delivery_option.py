from common.entities.customer_delivery import CustomerDelivery


class DeliveryOption:

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries
