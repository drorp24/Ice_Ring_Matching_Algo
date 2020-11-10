from dataclasses import dataclass
from pprint import pprint
from random import Random
from typing import Union, List

from common.entities.base_entities.distribution import Range
from common.entities.delivery_request import DeliveryRequestDistribution, DeliveryRequest


@dataclass
class DeliveryRequestDatasetStructure:
    num_of_delivery_requests: Union[int, Range] = 2
    num_of_delivery_options_per_delivery_request: Union[int, Range] = 7
    num_of_customer_deliveries_per_delivery_option: Union[int, Range] = 3
    num_of_package_delivery_plan_per_customer_delivery: Union[int, Range] = 5
    delivery_request_distribution: DeliveryRequestDistribution = \
        DeliveryRequestDistribution()


class DeliveryRequestDatasetGenerator:

    @staticmethod
    def generate(dr_struct: DeliveryRequestDatasetStructure = DeliveryRequestDatasetStructure()) -> List[DeliveryRequest]:
        dr_distrib = dr_struct.delivery_request_distribution
        return dr_distrib.choose_rand(random=Random(),
                                      amount=dr_struct.num_of_delivery_requests,
                                      num_do=dr_struct.num_of_delivery_options_per_delivery_request,
                                      num_cd=dr_struct.num_of_customer_deliveries_per_delivery_option,
                                      num_pdp=dr_struct.num_of_package_delivery_plan_per_customer_delivery)

