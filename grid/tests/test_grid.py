import unittest

from geometry.geo_factory import create_point_2d, create_polygon_2d
from grid.grid_location import GridLocation
from grid.grid_service import GridService


class BasicGridTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass


class BasicGridServiceTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p1 = create_point_2d(21.0, 21.0)
        cls.grid_location_1 = GridLocation(10, 10)

        cls.p2 = create_point_2d(0.0, 0.0)
        cls.p3 = create_point_2d(0.0, 40.0)
        cls.p4 = create_point_2d(40.0, 40.0)
        cls.p5 = create_point_2d(40.0, 0.0)
        cls.poly1 = create_polygon_2d([cls.p2, cls.p3, cls.p4, cls.p5])

    def test_get_grid_location(self):
        grid_location = GridService.get_grid_location(self.p1, 2)
        self.assertEqual(self.grid_location_1, grid_location)

    def test_get_polygon_centroid_grid_location(self):
        grid_location = GridService.get_polygon_centroid_grid_location(self.poly1, 2)
        self.assertEqual(self.grid_location_1, grid_location)
