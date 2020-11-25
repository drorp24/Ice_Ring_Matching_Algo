from dataclasses import dataclass
from random import Random
from typing import List

from common.entities.delivery_request import DeliveryRequestDistribution, DeliveryRequest


@dataclass
class DeliveryRequestDatasetStructure:
    num_of_delivery_requests: int = 2
    num_of_delivery_options_per_delivery_request: int = 5
    num_of_customer_deliveries_per_delivery_option: int = 10
    num_of_package_delivery_plan_per_customer_delivery: int = 3
    delivery_request_distribution: DeliveryRequestDistribution = DeliveryRequestDistribution()


class DeliveryRequestDatasetGenerator:

    @staticmethod
    def generate(dr_struct: DeliveryRequestDatasetStructure = DeliveryRequestDatasetStructure(),
                 random: Random = Random()) -> List[DeliveryRequest]:
        dr_distrib = dr_struct.delivery_request_distribution
        return dr_distrib.choose_rand(random=random,
                                      amount=dr_struct.num_of_delivery_requests,
                                      num_do=dr_struct.num_of_delivery_options_per_delivery_request,
                                      num_cd=dr_struct.num_of_customer_deliveries_per_delivery_option,
                                      num_pdp=dr_struct.num_of_package_delivery_plan_per_customer_delivery)