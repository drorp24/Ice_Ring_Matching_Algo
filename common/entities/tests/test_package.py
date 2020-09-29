import unittest
from matplotlib.patches import Circle
from math import cos, sin

from common.entities.package import PackageType, Package
from common.entities.package_factory import package_delivery_plan_factory
from common.math.angle import Angle, AngleUnit
from geometry.geo_factory import create_point_2d, create_polygon_2d
from geometry.shapely_wrapper import _ShapelyUtils
from visualization.drawer2d_factory import create_drawer2d


class BasicPackageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = Package(PackageType.TINY)
        cls.p2 = Package(PackageType.SMALL)
        cls.p3 = Package(PackageType.MEDIUM)
        cls.p4 = Package(PackageType.LARGE)
        point = create_point_2d(1,2)
        cls.pdp = package_delivery_plan_factory(point,
                                                azimuth=Angle(30, AngleUnit.DEGREE),
                                                elevation=Angle(80, AngleUnit.DEGREE),
                                                package_type=PackageType.TINY)
        cls.drone_azimuth = Angle(cls.pdp.azimuth.in_degrees() + 35, AngleUnit.DEGREE)

    def test_package_type(self):
        self.assertEqual(self.p1.type.value, 1)
        self.assertEqual(self.p2.type.value, 2)
        self.assertEqual(self.p3.type.value, 4)
        self.assertEqual(self.p4.type.value, 8)

    def test_package_delivery_plan(self):
        self.assertEqual(self.pdp.package.type.value, 1)

    def test_drop_envelope(self):
        drawer = create_drawer2d()
        drawer.add_point2d(self.pdp.drop_point.coordinates)
        minimal_potential_drop_envelope_circle = Circle(self.pdp.drop_point.coordinates.xy(),
                                                        self.pdp.package.potential_drop_envelope.minimal_radius_meters)
        drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
            minimal_potential_drop_envelope_circle.get_verts())))
        maximal_potential_drop_envelope_circle = Circle(self.pdp.drop_point.coordinates.xy(),
                                                        self.pdp.package.potential_drop_envelope.maximal_radius_meters)
        drawer.add_polygon2d(create_polygon_2d(_ShapelyUtils.convert_xy_array_to_points_list(
            maximal_potential_drop_envelope_circle.get_verts())))
        drawer.add_arrow2d(create_point_2d(self.pdp.drop_point.coordinates.x - cos(self.pdp.azimuth.in_radians()),
                                           self.pdp.drop_point.coordinates.y - sin(self.pdp.azimuth.in_radians())),
                            self.pdp.drop_point.coordinates)
        drop_envelope = self.pdp.drop_envelope(self.drone_azimuth)
        arrival_point = create_point_2d(self.pdp.drop_point.coordinates.x - self.pdp.package.potential_drop_envelope.maximal_radius_meters * cos(self.drone_azimuth.in_radians()),
                                        self.pdp.drop_point.coordinates.y - self.pdp.package.potential_drop_envelope.maximal_radius_meters * sin(self.drone_azimuth.in_radians()))
        drawer.add_arrow2d(create_point_2d(arrival_point.x - cos(self.drone_azimuth.in_radians()),
                                           arrival_point.y - sin(self.drone_azimuth.in_radians())), arrival_point)
        drawer.add_polygon2d(drop_envelope, edgecolor='green', facecolor='green')
        drawer.draw()
