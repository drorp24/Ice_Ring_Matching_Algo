from dataclasses import dataclass
from typing import List
from uuid import UUID

from optional import Optional

from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.math.angle import Angle
from grid.grid_location import GridLocation


@dataclass
class GridCell:
    location: Optional.of(GridLocation)


class EnvelopeGridCell(GridCell):

    def __init__(self, location: Optional.of(GridLocation), drone_azimuth: Angle, package_delivery_plans: List[PackageDeliveryPlan]):
        super().__init__(location)
        self._drone_azimuth = drone_azimuth
        self._package_delivery_plans = package_delivery_plans

    @property
    def drone_azimuth(self) -> Angle:
        return self._drone_azimuth

    @property
    def package_delivery_plans(self) -> List[PackageDeliveryPlan]:
        return self._package_delivery_plans

    def package_delivery_plans_ids(self) -> List[UUID]:
        return [package_delivery_plan.id for package_delivery_plan in self._package_delivery_plans]

