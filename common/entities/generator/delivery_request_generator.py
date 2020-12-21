from dataclasses import dataclass
from random import Random
from typing import List

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from geometry.geo_factory import create_point_2d


@dataclass
class DeliveryRequestDatasetStructure:
    num_of_delivery_requests: int = 2
    num_of_delivery_options_per_delivery_request: int = 5
    num_of_customer_deliveries_per_delivery_option: int = 10
    num_of_package_delivery_plan_per_customer_delivery: int = 3
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
                                      base_location=create_point_2d(0, 0),
                                      amount=dr_struct.get_amounts_as_dict())
