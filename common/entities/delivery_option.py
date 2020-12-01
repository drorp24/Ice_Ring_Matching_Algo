from random import Random
from typing import List

from common.entities.base_entity import JsonableBaseEntity
from common.entities.customer_delivery import CustomerDelivery, CustomerDeliveryDistribution, DEFAULT_PDP_DISTRIB
from common.entities.disribution.distribution import UniformChoiceDistribution, Distribution
from common.entities.package import PackageType
from geometry.geo2d import Point2D
from geometry.geo_distribution import PointLocationDistribution, UniformPointInBboxDistribution, \
    DEFAULT_ZERO_LOCATION_DISTRIBUTION
from geometry.geo_factory import calc_centroid, create_point_2d


class DeliveryOption(JsonableBaseEntity):

    def __init__(self, customer_deliveries: [CustomerDelivery]):
        self._customer_deliveries = customer_deliveries if customer_deliveries is not None else []

    @property
    def customer_deliveries(self) -> [CustomerDelivery]:
        return self._customer_deliveries

    def calc_location(self) -> Point2D:
        return calc_centroid([cd.calc_location() for cd in self.customer_deliveries])

    def get_amount_of_package_type(self, package_type: PackageType) -> int:
        customer_deliveries = self.customer_deliveries
        demands = list(map(lambda x: x.get_amount_of_package_type(package_type), customer_deliveries))
        return sum(demands)

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


loc_distrib = UniformPointInBboxDistribution(0, 0, 100, 100)
DEFAULT_CD_DISTRIB = CustomerDeliveryDistribution(relative_location_distribution=loc_distrib,
                                                  package_delivery_plan_distributions=[DEFAULT_PDP_DISTRIB])


class DeliveryOptionDistribution(Distribution):
    def __init__(self,
                 relative_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
                 customer_delivery_distributions: List[CustomerDeliveryDistribution] = DEFAULT_CD_DISTRIB):
        self._relative_location_distribution = relative_location_distribution
        self._customer_delivery_distributions = customer_delivery_distributions

    def choose_rand(self, random: Random, base_location: Point2D = create_point_2d(0, 0),
                    amount: int = 1, num_cd: int = 1, num_pdp: int = 1) -> List[DeliveryOption]:
        relative_locations = self._relative_location_distribution.choose_rand(random, amount)
        cd_distributions = UniformChoiceDistribution(self._customer_delivery_distributions).choose_rand(random, 1)[0]
        return [DeliveryOption(
            cd_distributions.choose_rand(random, base_location=base_location + relative_locations[i], amount=num_cd,
                                         num_pdp=num_pdp)) for i in list(range(amount))]
