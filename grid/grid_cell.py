from dataclasses import dataclass

from optional import Optional

from common.entities.package_delivery_plan import PackageDeliveryPlanList
from common.math.angle import Angle
from grid.grid_location import GridLocation


@dataclass
class GridCell:
    location: Optional.of(GridLocation)


@dataclass
class EnvelopeGridCell(GridCell):
    drone_azimuth: Angle
    package_delivery_plans: PackageDeliveryPlanList = PackageDeliveryPlanList([])
