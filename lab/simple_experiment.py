from math import cos, sin

from matplotlib.patches import Circle

from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d, create_polygon_2d
from geometry.shapely_wrapper import _ShapelyUtils
from visualization.drawer2d import Drawer2D
from visualization.drawer2d_factory import create_drawer2d


def draw_delivery_plan(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan):
    drawer.add_point2d(delivery_plan.drop_point.coordinates)
    minimal_potential_drop_envelope_circle = Circle(delivery_plan.drop_point.coordinates.xy(),
                                                    delivery_plan.package.potential_drop_envelope.minimal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
        minimal_potential_drop_envelope_circle.get_verts())), edgecolor='red', facecolor='red')
    maximal_potential_drop_envelope_circle = Circle(delivery_plan.drop_point.coordinates.xy(),
                                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
        maximal_potential_drop_envelope_circle.get_verts())), edgecolor='red', facecolor='white')
    drawer.add_arrow2d(create_point_2d(delivery_plan.drop_point.coordinates.x - cos(delivery_plan.azimuth.in_radians()),
                                       delivery_plan.drop_point.coordinates.y - sin(delivery_plan.azimuth.in_radians())),
                       delivery_plan.drop_point.coordinates, edgecolor='red', facecolor='red')


def draw_drone_arrival(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan, drone_azimuth: Angle):
    drone_arrival_angle_in_rad = Angle(180 + drone_azimuth.in_degrees(), AngleUnit.DEGREE).in_radians()
    arrival_point = create_point_2d(delivery_plan.drop_point.coordinates.x +
                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters *
                                    cos(drone_arrival_angle_in_rad),
                                    delivery_plan.drop_point.coordinates.y +
                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters *
                                    sin(drone_arrival_angle_in_rad))
    drawer.add_arrow2d(create_point_2d(arrival_point.x + 5*cos(drone_arrival_angle_in_rad),
                                       arrival_point.y + 5*sin(drone_arrival_angle_in_rad)),
                       arrival_point,
                       edgecolor='blue', linewidth=2)


def draw_drop_envelope(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan, drone_azimuth: Angle):
    drop_envelope = delivery_plan.drop_envelope(drone_azimuth)
    drawer.add_polygon2d(polygon2d=drop_envelope, edgecolor='green', facecolor='green')


def draw_delivery_envelope(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan,
                           drone_location: Point2D, drone_azimuth: Angle):
    delivery_envelope = delivery_plan.delivery_envelope(drone_location, drone_azimuth)
    drawer.add_polygon2d(delivery_envelope, edgecolor='blue', facecolor='blue')


def main():
    point = create_point_2d(1, 2)
    delivery_plan = package_delivery_plan_factory(point,
                                                  azimuth=Angle(30, AngleUnit.DEGREE),
                                                  elevation=Angle(80, AngleUnit.DEGREE),
                                                  package_type=PackageType.TINY)

    drone_azimuth = Angle(delivery_plan.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
    drawer = create_drawer2d()
    draw_delivery_plan(drawer, delivery_plan)
    draw_drone_arrival(drawer, delivery_plan, drone_azimuth)
    draw_drop_envelope(drawer, delivery_plan, drone_azimuth)
    drone_location = create_point_2d(-244.87809284739458, -915.6295349746149)
    draw_delivery_envelope(drawer, delivery_plan, drone_location, drone_azimuth)
    drawer.draw(block=False)

    drone_azimuth = Angle(delivery_plan.azimuth.in_degrees(), AngleUnit.DEGREE)
    drawer2 = create_drawer2d()
    draw_delivery_plan(drawer2, delivery_plan)
    draw_drone_arrival(drawer2, delivery_plan, drone_azimuth)
    draw_drop_envelope(drawer2, delivery_plan, drone_azimuth)
    drone_location = create_point_2d(-821.7241335952167, -473.0000000000001)
    draw_delivery_envelope(drawer2, delivery_plan, drone_location, drone_azimuth)
    drawer2.draw(block=True)


if __name__ == "__main__":
    main()
