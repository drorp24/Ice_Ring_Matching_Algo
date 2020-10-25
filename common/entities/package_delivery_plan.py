from attr import dataclass

from common.entities.customer_delivery import CustomerDeliveryId
from common.entities.delivery_option import DeliveryOptionId
from common.entities.delivery_request import DeliveryRequestId
from common.entities.package import PackageType
from geometry.geo2d import Point2D, Polygon2D
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_vector_2d, create_polygon_2d_from_ellipse

import statistics
from math import cos, sin

@dataclass
class PackageDeliveryPlanKey:
    delivery_request_id: DeliveryRequestId
    delivery_option_id: DeliveryOptionId
    customer_delivery_id: CustomerDeliveryId

class PackageDeliveryPlan:

    def __init__(self, drop_point: Point2D, azimuth: Angle, elevation: Angle, package_type: PackageType):
        self._drop_point = drop_point
        self._azimuth = azimuth
        self._elevation = elevation
        self._package_type = package_type

    def __eq__(self, other):
        return (self.drop_point == other.drop_point) and \
               (self.azimuth == other.azimuth) and \
               (self.elevation == other.elevation) and \
               (self.package_type == other.package_type)

    @property
    def drop_point(self) -> Point2D:
        return self._drop_point

    @property
    def azimuth(self) -> Angle:
        return self._azimuth

    @property
    def elevation(self) -> Angle:
        return self._elevation

    @property
    def package_type(self) -> PackageType:
        return self._package_type

