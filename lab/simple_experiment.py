import statistics
from math import cos, sin
from matplotlib.patches import Circle

from common.entities.package import PackageType, PotentialDropEnvelope
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo2d import Point2D
from geometry.geo_factory import create_point_2d, create_polygon_2d
from geometry.utils import GeometryUtils
from visualization.color import Color
from visualization.drawer2d import Drawer2D
from visualization.drawer2d_factory import create_drawer2d


def draw_potential_drop_envelope(drawer: Drawer2D, potential_drop_envelope: PotentialDropEnvelope, location: Point2D):
    minimal_potential_drop_envelope_circle = Circle((location.xy()),
                                                    potential_drop_envelope.minimal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
        minimal_potential_drop_envelope_circle.get_verts())), edgecolor=Color.Red, facecolor=Color.Red)
    maximal_potential_drop_envelope_circle = Circle(location.xy(),
                                                    potential_drop_envelope.maximal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(GeometryUtils.convert_xy_array_to_points_list(
        maximal_potential_drop_envelope_circle.get_verts())), edgecolor=Color.Red, facecolor=Color.White)


def draw_location_azimuth(drawer: Drawer2D, location: Point2D, azimuth: Angle, color):
    drawer.add_arrow2d(create_point_2d(location.x - cos(azimuth.in_radians()),
                                       location.y - sin(azimuth.in_radians())),
                       location, edgecolor=color, facecolor=color)


def draw_delivery_plan(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan):
    drawer.add_point2d(delivery_plan.drop_point)
    draw_potential_drop_envelope(drawer,
                                 delivery_plan.package.potential_drop_envelope,
                                 delivery_plan.drop_point)
    draw_location_azimuth(drawer, delivery_plan.drop_point, delivery_plan.azimuth, Color.Red)


def draw_drone_arrival(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan, drone_azimuth: Angle):
    drone_arrival_angle = Angle(180 + drone_azimuth.in_degrees(), AngleUnit.DEGREE)
    arrival_point = create_point_2d(delivery_plan.drop_point.x +
                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters *
                                    cos(drone_arrival_angle.in_radians()),
                                    delivery_plan.drop_point.y +
                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters *
                                    sin(drone_arrival_angle.in_radians()))
    draw_location_azimuth(drawer, arrival_point, drone_azimuth, Color.Blue)


def draw_drop_envelope(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan, drone_azimuth: Angle):
    drop_envelope = delivery_plan.drop_envelope(drone_azimuth)
    drawer.add_polygon2d(polygon2d=drop_envelope, edgecolor=Color.Green, facecolor=Color.Green)


def draw_delivery_envelope(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan,
                           drone_location: Point2D, drone_azimuth: Angle):
    delivery_envelope = delivery_plan.delivery_envelope(drone_location, drone_azimuth)
    drawer.add_polygon2d(delivery_envelope, edgecolor=Color.Blue, facecolor=Color.Blue)
    average_radius = statistics.mean([delivery_plan.package.potential_drop_envelope.maximal_radius_meters,
                                      delivery_plan.package.potential_drop_envelope.minimal_radius_meters])
    envelope_center = create_point_2d(drone_location.x +
                                      (average_radius * cos(drone_azimuth.in_radians())),
                                      drone_location.y +
                                      (average_radius * sin(drone_azimuth.in_radians())))
    draw_location_azimuth(drawer, envelope_center, delivery_plan.azimuth, Color.Red)


def main():
    # Experiment 1
    drop_point = create_point_2d(1, 2)
    delivery_plan = package_delivery_plan_factory(drop_point,
                                                  azimuth=Angle(30, AngleUnit.DEGREE),
                                                  elevation=Angle(80, AngleUnit.DEGREE),
                                                  package_type=PackageType.TINY)
    drone_azimuth1 = Angle(delivery_plan.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
    drawer1 = create_drawer2d()
    draw_delivery_plan(drawer1, delivery_plan)
    draw_drone_arrival(drawer1, delivery_plan, drone_azimuth1)
    draw_drop_envelope(drawer1, delivery_plan, drone_azimuth1)
    drawer1.draw(block=False)

    # # Experiment 2
    drawer2 = create_drawer2d()
    drone_location2 = create_point_2d(0, -1000)
    draw_potential_drop_envelope(drawer2, delivery_plan.package.potential_drop_envelope, drone_location2)
    drone_azimuth2 = Angle(90, AngleUnit.DEGREE)
    draw_drone_arrival(drawer2, delivery_plan, drone_azimuth2)
    draw_delivery_envelope(drawer2, delivery_plan, drone_location2, drone_azimuth2)
    drawer2.draw(block=False)

    # Experiment 3
    drone_azimuth3 = Angle(delivery_plan.azimuth.in_degrees(), AngleUnit.DEGREE)
    drawer3 = create_drawer2d()
    draw_delivery_plan(drawer3, delivery_plan)
    draw_drone_arrival(drawer3, delivery_plan, drone_azimuth3)
    draw_drop_envelope(drawer3, delivery_plan, drone_azimuth3)
    drawer3.draw(block=False)

    # Experiment 4
    drone_azimuth4 = Angle(delivery_plan.azimuth.in_degrees() + 100, AngleUnit.DEGREE)
    drawer4 = create_drawer2d()
    draw_delivery_plan(drawer4, delivery_plan)
    draw_drone_arrival(drawer4, delivery_plan, drone_azimuth4)
    draw_drop_envelope(drawer4, delivery_plan, drone_azimuth4)
    drawer4.draw(block=True)


if __name__ == "__main__":
    main()
