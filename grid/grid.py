from typing import List
import numpy as np

from common.entities.delivery_request import DeliveryRequest
from grid.cell import DeliveryRequestEnvelopeCells, CellServices, AzimuthOptions
from grid.slides_container import SlidesContainer
from services.delivery_request_distance_service_interface import DeliveryRequestDistanceServiceInterface


class DeliveryRequestsGrid(DeliveryRequestDistanceServiceInterface):
    def __init__(self, slides_container: SlidesContainer, delivery_requests: List[DeliveryRequest]):
        self.delivery_requests_envelope_cells = \
            self._create_delivery_requests_envelope_cells(slides_container, delivery_requests)

    @staticmethod
    def _create_delivery_requests_envelope_cells(self, slides_container, delivery_requests):
        return {delivery_request: DeliveryRequestEnvelopeCells(slides_container, delivery_request)
                for delivery_request in delivery_requests}

    def get_distance(self, delivery_request1: DeliveryRequest, delivery_request2: DeliveryRequest,
                     delivery_request1_selected_option: int, delivery_request2_selected_option: int) -> float:
        delivery_request1_envelope_cells = \
            self.delivery_requests_envelope_cells[
                delivery_request1].delivery_request_envelope_cells[delivery_request1_selected_option]
        delivery_request2_envelope_cells = self.delivery_requests_envelope_cells[
            delivery_request2].delivery_request_envelope_cells[delivery_request2_selected_option]
        delivery_request1_envelope_cells
        delivery_request_1_cells = delivery_request1_envelope_cells.values()
        delivery_request_2_cells = delivery_request2_envelope_cells.values()
        return sum([CellServices.get_distance(cell_1, cell_2) for cell_1, cell_2 in
                    zip(delivery_request_1_cells, delivery_request_2_cells) if cell_1.location != cell_2.location])
