from math import cos, sin

from matplotlib.patches import Circle

from common.entities.package import PackageType
from common.entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_polygon_2d
from geometry.shapely_wrapper import _ShapelyUtils
from visualization.drawer2d import Drawer2D
from visualization.drawer2d_factory import create_drawer2d


def draw_delivery_plan(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan):
    drawer.add_point2d(delivery_plan.drop_point.coordinates)
    minimal_potential_drop_envelope_circle = Circle(delivery_plan.drop_point.coordinates.xy(),
                                                    delivery_plan.package.potential_drop_envelope.minimal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
        minimal_potential_drop_envelope_circle.get_verts())))
    maximal_potential_drop_envelope_circle = Circle(delivery_plan.drop_point.coordinates.xy(),
                                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters)
    drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
        maximal_potential_drop_envelope_circle.get_verts())))
    drawer.add_arrow2d(create_point_2d(delivery_plan.drop_point.coordinates.x - cos(delivery_plan.azimuth.in_radians()),
                                       delivery_plan.drop_point.coordinates.y - sin(delivery_plan.azimuth.in_radians())),
                       delivery_plan.drop_point.coordinates)


def draw_drop_envelope(drawer: Drawer2D, delivery_plan: PackageDeliveryPlan, drone_azimuth: Angle):
    drop_envelope = delivery_plan.drop_envelope(drone_azimuth)
    arrival_point = create_point_2d(delivery_plan.drop_point.coordinates.x -
                                    delivery_plan.package.potential_drop_envelope.maximal_radius_meters * cos(drone_azimuth.in_radians()),
                                    delivery_plan.drop_point.coordinates.y - delivery_plan.package.potential_drop_envelope.maximal_radius_meters * sin
            (drone_azimuth.in_radians()))
    drawer.add_arrow2d(create_point_2d(arrival_point.x - cos(drone_azimuth.in_radians()),
                                       arrival_point.y - sin(drone_azimuth.in_radians())), arrival_point)
    drawer.add_polygon2d(drop_envelope, edgecolor='green', facecolor='green')


def main():
    point = create_point_2d(1, 2)
    delivery_plan = package_delivery_plan_factory(point,
                                                  azimuth=Angle(30, AngleUnit.DEGREE),
                                                  elevation=Angle(80, AngleUnit.DEGREE),
                                                  package_type=PackageType.TINY)

    drone_azimuth = Angle(delivery_plan.azimuth.in_degrees() + 45, AngleUnit.DEGREE)
    drawer = create_drawer2d()
    draw_delivery_plan(drawer, delivery_plan)
    draw_drop_envelope(drawer, delivery_plan, drone_azimuth)
    drawer.draw()


if __name__ == "__main__":
    main()
