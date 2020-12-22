from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.disribution.distribution import UniformChoiceDistribution, Distribution
from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanDistribution, \
    DEFAULT_AZI_DISTRIB, DEFAULT_PITCH_DISTRIB, DEFAULT_PACKAGE_DISTRIB
from geometry.geo2d import Point2D, Polygon2D
from geometry.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import calc_centroid, calc_convex_hull_polygon, create_point_2d
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

    def get_package_type_volume(self, package_type: PackageType) -> int:
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


DEFAULT_RELATIVE_DROP_POINT_DISTRIB = DEFAULT_ZERO_LOCATION_DISTRIBUTION
DEFAULT_PDP_DISTRIB = PackageDeliveryPlanDistribution(DEFAULT_RELATIVE_DROP_POINT_DISTRIB,
                                                      DEFAULT_AZI_DISTRIB,
                                                      DEFAULT_PITCH_DISTRIB,
                                                      DEFAULT_PACKAGE_DISTRIB)


class CustomerDeliveryDistribution(Distribution):
    def __init__(self, relative_location_distribution: PointLocationDistribution = DEFAULT_RELATIVE_DROP_POINT_DISTRIB,
                 package_delivery_plan_distributions: [PackageDeliveryPlanDistribution] = [DEFAULT_PDP_DISTRIB]):
        self._relative_location_distribution = relative_location_distribution
        self._pdp_distributions = package_delivery_plan_distributions

    def choose_rand(self, random: Random, base_loc: Point2D = create_point_2d(0, 0),
                    amount: int = 1, num_pdp: int = 1) -> List[CustomerDelivery]:
        relative_locations = self._relative_location_distribution.choose_rand(random=random, amount=amount)
        pdp_distribution = UniformChoiceDistribution(self._pdp_distributions).choose_rand(random=random, amount=1)[0]
        # TODO: calculate single package delivery type for each pdp distribution in customer delivery
        return [CustomerDelivery(
            pdp_distribution.choose_rand(random=random, amount=num_pdp, base_loc=base_loc + relative_locations[i]))
            for i in list(range(amount))]
