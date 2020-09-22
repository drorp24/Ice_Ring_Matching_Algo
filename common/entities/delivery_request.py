class DeliveryRequest:

    def __init__(self):
        self._type = 'DeliveryRequest'

    @property
    def type(self) -> str:
        return self._type