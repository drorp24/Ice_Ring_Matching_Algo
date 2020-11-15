from typing import List

from common.entities.delivery_request import DeliveryRequest
from grid.cell import DeliveryRequestEnvelopeCells, CellServices
from grid.slides_container import SlidesContainer
from services.delivery_request_distance_service_interface import DeliveryRequestDistanceServiceInterface


class DeliveryRequestsGrid (DeliveryRequestDistanceServiceInterface):
    def __init__(self, slides_container: SlidesContainer, delivery_requests: List[DeliveryRequest]):
        self.delivery_requests_envelope_cells = self._create_delivery_requests_envelope_cells(slides_container, delivery_requests)

    def _create_delivery_requests_envelope_cells(self, slides_container, delivery_requests):
        return {delivery_request.id: DeliveryRequestEnvelopeCells(slides_container, delivery_request) for delivery_request in delivery_requests}

    def get_distance(self, delivery_request1: DeliveryRequest, delivery_request2: DeliveryRequest) -> float:
        delivery_request1_envelope_cells = self.delivery_requests_envelope_cells[delivery_request1.id].delivery_requests_envelope_cells[0]    #todo Select option
        delivery_request2_envelope_cells = self.delivery_requests_envelope_cells[delivery_request2.id].delivery_requests_envelope_cells[0]    #todo Select option
        return min ([CellServices.get_distance() for angle1, cell1 in delivery_request1_envelope_cells.items() for angle2, cell2 in delivery_request2_envelope_cells.items()])
