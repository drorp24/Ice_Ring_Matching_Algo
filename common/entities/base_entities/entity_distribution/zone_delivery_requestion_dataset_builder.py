from typing import List

from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DEFAULT_DR_PRIORITY_DISTRIB, \
    PriorityDistribution, DEFAULT_TW_DR_DISRIB
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import DEFAULT_PITCH_DISTRIB, \
    DEFAULT_AZI_DISTRIB, DEFAULT_PACKAGE_DISTRIB, PackageDeliveryPlanDistribution
from common.entities.base_entities.entity_distribution.package_distribution import PackageDistribution
from common.entities.base_entities.entity_distribution.temporal_distribution import TimeWindowDistribution
from common.entities.base_entities.entity_distribution.zone_delivery_request_distribution import \
    ZoneDeliveryRequestDistribution
from common.entities.base_entities.zone import Zone
from common.math.angle import AngleUniformDistribution
from geometry.distribution.geo_distribution import PointLocationDistribution, DEFAULT_ZERO_LOCATION_DISTRIBUTION


def build_zone_delivery_request_distribution(
        zones: List[Zone],
        relative_dr_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_do_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_cd_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        relative_pdp_location_distribution: PointLocationDistribution = DEFAULT_ZERO_LOCATION_DISTRIBUTION,
        azimuth_distribution: AngleUniformDistribution = DEFAULT_AZI_DISTRIB,
        pitch_distribution: AngleUniformDistribution = DEFAULT_PITCH_DISTRIB,
        package_type_distribution: PackageDistribution = DEFAULT_PACKAGE_DISTRIB,
        priority_distribution: PriorityDistribution = DEFAULT_DR_PRIORITY_DISTRIB,
        time_window_distribution: TimeWindowDistribution = DEFAULT_TW_DR_DISRIB) -> ZoneDeliveryRequestDistribution:
    pdp_distributions = [PackageDeliveryPlanDistribution(
        relative_location_distribution=relative_pdp_location_distribution,
        azimuth_distribution=azimuth_distribution,
        pitch_distribution=pitch_distribution,
        package_type_distribution=package_type_distribution)]
    cd_distributions = [CustomerDeliveryDistribution(
        package_delivery_plan_distributions=pdp_distributions,
        relative_location_distribution=relative_cd_location_distribution)]
    do_distributions = [DeliveryOptionDistribution(
        customer_delivery_distributions=cd_distributions,
        relative_location_distribution=relative_do_location_distribution)]
    return ZoneDeliveryRequestDistribution(
        zones=zones,
        delivery_option_distributions=do_distributions,
        priority_distribution=priority_distribution,
        time_window_distributions=time_window_distribution,
        relative_location_distribution=relative_dr_location_distribution)
