import itertools
from typing import List

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.drone import PackageTypeAmountMap
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from geometry.geo2d import Point2D
from geometry.geo_factory import calc_centroid
from geometry.utils import Localizable


class DeliveryOption(JsonableBaseEntity, Localizable):

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return list(itertools.chain.from_iterable(
            customer_delivery.package_delivery_plans for customer_delivery in self.customer_deliveries))

    def calc_location(self) -> Point2D:
        return calc_centroid([cd.calc_location() for cd in self.customer_deliveries])

    def get_package_type_amount(self, package_type: PackageType) -> int:
        customer_deliveries = self.customer_deliveries
        demands = list(map(lambda x: x.get_package_type_amount(package_type), customer_deliveries))
        return sum(demands)

    def get_package_type_amount_map(self) -> PackageTypeAmountMap:
        return PackageTypeAmountMap([self.get_package_type_amount(package_type) for package_type in PackageType])

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return DeliveryOption(
            customer_deliveries=[CustomerDelivery.dict_to_obj(cd_dict) for cd_dict in
                                 dict_input['customer_deliveries']])

    def __eq__(self, other):
        return self.customer_deliveries == other.customer_deliveries

    def __hash__(self):
        return hash(tuple(self.customer_deliveries))
