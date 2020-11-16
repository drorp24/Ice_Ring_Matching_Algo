from typing import List
import numpy as np

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
        delivery_request1_selected_option = 0   #todo Select option
        delivery_request2_selected_option = 0   #todo Select option
        delivery_request1_envelope_cells = self.delivery_requests_envelope_cells[delivery_request1.id].delivery_request_envelope_cells[delivery_request1_selected_option]
        delivery_request2_envelope_cells = self.delivery_requests_envelope_cells[delivery_request2.id].delivery_request_envelope_cells[delivery_request2_selected_option]


        # delivery_request1_package_delivery_plan_ids = [package_delivery_plan.id for package_delivery_plan in delivery_request1.delivery_options[delivery_request1_selected_option].package_delivery_plans]
        # delivery_request2_package_delivery_plan_ids = [package_delivery_plan.id for package_delivery_plan in delivery_request2.delivery_options[delivery_request2_selected_option].package_delivery_plans]


        delivery_request1_package_delivery_plan_ids = list(
            range(len(delivery_request1.delivery_options[delivery_request1_selected_option].package_delivery_plans)))
        delivery_request2_package_delivery_plan_ids = list(
            range(len(delivery_request2.delivery_options[delivery_request2_selected_option].package_delivery_plans)))

        for angle in delivery_request1_envelope_cells.keys():
            if not delivery_request1_package_delivery_plan_ids and not delivery_request2_package_delivery_plan_ids:
                break
            if angle in delivery_request2_envelope_cells and \
                    delivery_request1_envelope_cells[angle].location == delivery_request2_envelope_cells[
                angle].location:
                for package_delivery_plan_id in delivery_request1_envelope_cells[angle].package_delivery_plan_ids:
                    if package_delivery_plan_id in delivery_request1_package_delivery_plan_ids:
                        delivery_request1_package_delivery_plan_ids.remove(package_delivery_plan_id)
                for package_delivery_plan_id in delivery_request2_envelope_cells[angle].package_delivery_plan_ids:
                    if package_delivery_plan_id in delivery_request2_package_delivery_plan_ids:
                        delivery_request2_package_delivery_plan_ids.remove(package_delivery_plan_id)

        return 0
        # distance_memorization = np.ones((8,8))* -1
        # for delivery_request1_package_delivery_plan_id in delivery_request1_package_delivery_plan_ids:
        #     for envelope_cell in delivery_request1_envelope_cells.values():
        #         if delivery_request1_package_delivery_plan_id in envelope_cell.package_delivery_plan_ids:
        #
        #
        #
        # return min ([CellServices.get_distance() for angle1, cell1 in delivery_request1_envelope_cells.items() for angle2, cell2 in delivery_request2_envelope_cells.items()])


