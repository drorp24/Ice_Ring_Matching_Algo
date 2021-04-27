from copy import deepcopy
from typing import List

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.base_entities.package_holder import PackageHolder
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_factory import calc_centroid, calc_convex_hull_polygon
from geometry.utils import Localizable


class CustomerDelivery(JsonableBaseEntity, Localizable, PackageHolder):

    def __init__(self, package_delivery_plans: List[PackageDeliveryPlan], customer_delivery_id: EntityID):
        self._id = customer_delivery_id
        self._package_delivery_plans = package_delivery_plans

    @property
    def id(self) -> EntityID:
        return self._id

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return self._package_delivery_plans

    def calc_location(self) -> Point2D:
        return calc_centroid([pdp.drop_point for pdp in self._package_delivery_plans])

    def calc_bounds(self) -> Polygon2D:
        return calc_convex_hull_polygon([pdp.drop_point for pdp in self._package_delivery_plans])

    def get_package_type_amount(self, package_type: PackageType) -> int:
        package_delivery_plans = self.package_delivery_plans
        return len(list(filter(lambda x: x.package_type == package_type, package_delivery_plans)))

    def __eq__(self, other):
        return self.package_delivery_plans == other.package_delivery_plans

    def __hash__(self):
        return hash(tuple(self.package_delivery_plans))

    def __deepcopy__(self, memodict={}):
        new_copy = CustomerDelivery(deepcopy(self.package_delivery_plans, memodict), deepcopy(self.id, memodict))
        memodict[id(self)] = new_copy
        return new_copy

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return CustomerDelivery(
            customer_delivery_id=EntityID.dict_to_obj(dict_input['id']),
            package_delivery_plans=[PackageDeliveryPlan.dict_to_obj(pdp_dict) for pdp_dict in
                                    dict_input['package_delivery_plans']])
