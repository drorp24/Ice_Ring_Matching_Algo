import unittest
from pathlib import Path

from matplotlib.testing.compare import compare_images

from geometry.geo_factory import create_polygon_2d, \
    create_point_2d, create_vector_2d, create_line_string_2d, \
    create_linear_ring_2d
from visualization.basic.drawer2d import Drawer2DCoordinateSys
from visualization.basic.pltdrawer2d import create_drawer_2d


class DrawGeometriesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(0.0, 0.0)
        cls.p2 = create_point_2d(0.0, 5.0)
        cls.p3 = create_point_2d(5.0, 5.0)
        cls.p4 = create_point_2d(5.0, 0.0)
        cls.p5 = create_point_2d(3.0, 5.0)
        cls.p6 = create_point_2d(3.0, 0.0)
        cls.p7 = create_point_2d(7.0, 8.0)
        cls.p8 = create_point_2d(6.0, 10.0)
        cls.v1 = create_vector_2d(2.0, 4.0)
        cls.line_string1 = create_line_string_2d([cls.p3, cls.p6, cls.p7, cls.p8])
        cls.poly1 = create_polygon_2d([cls.p1, cls.p2, cls.p3, cls.p4])
        cls.linear_ring1 = create_linear_ring_2d([cls.p1, cls.p2, cls.p5, cls.p6])
        base_path = 'visualization/basic/tests/images/'
        cls.expected_cartesian_image_path = Path('%sexpected_cartesian_drawer2d_output.png' % base_path)
        cls.actual_cartesian_image_path = Path('%sactual_cartesian_drawer2d_output.png' % base_path)
        cls.expected_geographic_image_path = Path('%sexpected_geographic_drawer2d_output.png' % base_path)
        cls.actual_geographic_image_path = Path('%sactual_geographic_drawer2d_output.png' % base_path)

    @classmethod
    def tearDownClass(cls):
        cls.actual_cartesian_image_path.unlink()
        cls.actual_geographic_image_path.unlink()

    def test_draw_when_coordinate_system_is_cartesian(self):
        drawer = create_drawer_2d(Drawer2DCoordinateSys.CARTESIAN)

        drawer.add_point2d(self.p1)
        drawer.add_line_string2d(self.line_string1)
        drawer.add_polygon2d(self.poly1)
        drawer.add_linear_ring2d(self.linear_ring1)
        drawer.add_arrow2d(tail=self.p5, head=self.p8)
        drawer.add_text("test", self.p3)

        drawer.save_plot_to_png(self.actual_cartesian_image_path)
        self.assertIsNone(compare_images(self.expected_cartesian_image_path, self.actual_cartesian_image_path, tol=1))

    def test_draw_when_coordinate_system_is_geographic(self):
        drawer = create_drawer_2d(Drawer2DCoordinateSys.GEOGRAPHIC)

        drawer.add_point2d(self.p1)
        drawer.add_line_string2d(self.line_string1)
        drawer.add_polygon2d(self.poly1)
        drawer.add_linear_ring2d(self.linear_ring1)
        drawer.add_arrow2d(tail=self.p5, head=self.p8)
        drawer.add_text("test", self.p3)

        drawer.save_plot_to_png(self.actual_geographic_image_path)
        self.assertIsNone(compare_images(self.expected_geographic_image_path, self.actual_geographic_image_path, tol=1))
