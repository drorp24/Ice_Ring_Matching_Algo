class CustomerDelivery:

    def __init__(self):
        self._type = 'CustomerDelivery'

    @property
    def type(self) -> str:
        return self._type

    @property
    def package_delivery_plans(self) -> str:
        raise NotImplementedError()
