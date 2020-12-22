from dataclasses import dataclass
from random import Random
from typing import List, Union

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import Range
from geometry.geo_factory import create_zero_point_2d


@dataclass
class DeliveryRequestDatasetStructure:
    num_of_delivery_requests: Union[int, Range] = 2
    num_of_delivery_options_per_delivery_request: Union[int, Range] = 5
    num_of_customer_deliveries_per_delivery_option: Union[int, Range] = 10
    num_of_package_delivery_plan_per_customer_delivery: Union[int, Range] = 3
    delivery_request_distribution: DeliveryRequestDistribution = DeliveryRequestDistribution()

    def get_amounts_as_dict(self):
        return {
            DeliveryRequest: self.num_of_delivery_requests,
            DeliveryOption: self.num_of_delivery_options_per_delivery_request,
            CustomerDelivery: self.num_of_customer_deliveries_per_delivery_option,
            PackageDeliveryPlan: self.num_of_package_delivery_plan_per_customer_delivery
        }


class DeliveryRequestDatasetGenerator:

    @staticmethod
    def generate(dr_struct: DeliveryRequestDatasetStructure = DeliveryRequestDatasetStructure(),
                 random: Random = Random()) -> List[DeliveryRequest]:
        dr_distrib = dr_struct.delivery_request_distribution
        return dr_distrib.choose_rand(random=random,
                                      base_loc=create_zero_point_2d(),
                                      amount=dr_struct.get_amounts_as_dict())
