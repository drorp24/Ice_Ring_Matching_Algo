from dataclasses import dataclass
from typing import Union

from common.entities.base_entities.distribution import Range
from common.entities.customer_delivery import CustomerDeliveryDistribution
from common.entities.delivery_option import DeliveryOptionDistribution
from common.entities.delivery_request import DeliveryRequestDistribution
from common.entities.package_delivery_plan import PackageDeliveryPlanDistribution


@dataclass
class DeliveryRequestDatasetStructure:
    num_of_delivery_requests: Union[int, Range] = 1
    num_of_delivery_options_per_delivery_request: Union[int, Range] = 1
    num_of_customer_deliveries_per_delivery_option: Union[int, Range] = 1
    num_of_package_delivery_plan_per_delivery_option: Union[int, Range] = 1
    delivery_request_distribution: DeliveryRequestDistribution = DeliveryRequestDistribution()
    delivery_option_distribution: DeliveryOptionDistribution = DeliveryOptionDistribution()
    customer_delivery_distribution: CustomerDeliveryDistribution = CustomerDeliveryDistribution()
    package_delivery_plan_distribution: PackageDeliveryPlanDistribution = PackageDeliveryPlanDistribution()


# class DeliveryRequestDatasetGenerator:
