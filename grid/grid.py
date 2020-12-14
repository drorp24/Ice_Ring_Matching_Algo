import math
from statistics import mean
from typing import List
from common.entities.delivery_request import DeliveryRequest
from grid.grid_cell_services import GridCellServices
from grid.delivery_request_envelope_cells import DeliveryRequestPotentialEnvelopes
from grid.slides_container import SlidesContainer
from services.delivery_request_distance_service_interface import DeliveryRequestDistanceServiceInterface


class DeliveryRequestsGrid(DeliveryRequestDistanceServiceInterface):
    def __init__(self, slides_container: SlidesContainer, delivery_requests: List[DeliveryRequest]):
        self._delivery_requests_envelope_cells = \
            self._create_delivery_requests_envelope_cells(slides_container, delivery_requests)

    @property
    def delivery_requests_envelope_cells(self):
        return self._delivery_requests_envelope_cells

    @staticmethod
    def _create_delivery_requests_envelope_cells(slides_container, delivery_requests):
        return {delivery_request: DeliveryRequestPotentialEnvelopes(slides_container, delivery_request)
                for delivery_request in delivery_requests}

    def get_distance_between_delivery_options(self, delivery_request1: DeliveryRequest,
                                              delivery_request2: DeliveryRequest,
                                              delivery_request1_selected_option: int = 0,
                                              delivery_request2_selected_option: int = 0) -> float:
        delivery_request1_envelope_cells = \
            self.delivery_requests_envelope_cells[
                delivery_request1].delivery_options_cells[delivery_request1_selected_option]

        delivery_request2_envelope_cells = \
            self.delivery_requests_envelope_cells[
                delivery_request2].delivery_options_cells[delivery_request2_selected_option]

        delivery_request_1_cells = delivery_request1_envelope_cells.values()
        delivery_request_2_cells = delivery_request2_envelope_cells.values()
        distances_list_filter = list(filter(lambda dist: dist != math.inf,
                                            [GridCellServices.calc_distance(cell_1, cell_2) for cell_1, cell_2 in
                                             zip(delivery_request_1_cells,
                                                 delivery_request_2_cells)]))

        return mean(distances_list_filter) if distances_list_filter else math.inf
