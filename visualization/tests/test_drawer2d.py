import unittest
from matplotlib.testing.compare import compare_images
from pathlib import Path
from geometry.geo_factory import create_polygon_2d, \
    create_point_2d, create_vector_2d, create_line_string_2d, \
    create_linear_ring_2d
from visualization.drawer2d_factory import create_drawer2d


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
        cls.expected_image_path = Path('test_drawer2d_expected.png')
        cls.result_image_path = Path('test_drawer2d_actual.png')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.result_image_path.unlink()

    def test_draw(self):
        drawer = create_drawer2d()
        drawer.add_point2d(self.p1)
        drawer.add_vector2d(self.v1)
        drawer.add_line_string2d(self.line_string1)
        drawer.add_polygon2d(self.poly1)
        drawer.add_linear_ring2d(self.linear_ring1)
        #drawer.draw()

        drawer.save_plot_to_png(self.result_image_path)
        self.assertIsNone(compare_images(self.expected_image_path, self.result_image_path, tol=1))
