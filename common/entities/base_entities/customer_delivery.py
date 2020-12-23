from typing import List

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_factory import calc_centroid, calc_convex_hull_polygon
from geometry.utils import Localizable


class CustomerDelivery(JsonableBaseEntity, Localizable):

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan]):
        self._package_delivery_plans = package_delivery_plans

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return self._package_delivery_plans

    def calc_location(self) -> Point2D:
        return calc_centroid([pdp.drop_point for pdp in self._package_delivery_plans])

    def calc_bounds(self) -> Polygon2D:
        return calc_convex_hull_polygon([pdp.drop_point for pdp in self._package_delivery_plans])

    def get_amount_of_package_type(self, package_type: PackageType) -> int:
        package_delivery_plans = self.package_delivery_plans
        return len(list(filter(lambda x: x.package_type == package_type, package_delivery_plans)))

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    def __hash__(self):
        return hash(tuple(self.package_delivery_plans))

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return CustomerDelivery(
            package_delivery_plans=[PackageDeliveryPlan.dict_to_obj(pdp_dict) for pdp_dict in
                                    dict_input['package_delivery_plans']])
