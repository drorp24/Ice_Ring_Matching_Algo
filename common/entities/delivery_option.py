from common.entities.customer_delivery import CustomerDelivery


class DeliveryOption:

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        if not isinstance(customer_deliveries, list):
            raise TypeError("customer_deliveries must be a list")

        self._type = 'DeliveryOption'
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    @property
    def type(self) -> str:
        return self._type

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries
