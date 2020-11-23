import unittest

from optional import Optional

from grid.grid_location import GridLocation, GridLocationServices


class BasicGridLocationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.row = 10
        cls.column = 15

        cls.grid_location_1 = GridLocation(10, 15)
        cls.grid_location_2 = GridLocation(20, 10)
        cls.grid_location_3 = GridLocation(60, 5)

        cls.grid_location_avg = GridLocation(30, 10)

    def test_grid_location(self):
        self.assertEqual(self.row, self.grid_location_1.row)
        self.assertEqual(self.column, self.grid_location_1.column)

    def test_grid_location_calc_average(self):
        average_grid_location = GridLocationServices.calc_average(
            [self.grid_location_1, self.grid_location_2, self.grid_location_3])

        self.assertEqual(self.grid_location_avg, average_grid_location)

    def test_get_not_empty_indices(self):
        not_empty_indices = GridLocationServices.get_not_empty_indices(
            [Optional.of(self.grid_location_1), Optional.of(self.grid_location_2), Optional.empty(),
             Optional.of(self.grid_location_3)])

        self.assertEqual(len(not_empty_indices), 3)

    def test_get_not_empty_grid_locations(self):
        not_empty_grid_locations = GridLocationServices.get_not_empty_grid_locations(
            [Optional.of(self.grid_location_1), Optional.of(self.grid_location_2), Optional.empty(),
             Optional.of(self.grid_location_3)])

        expected_not_empty_grid_locations = [self.grid_location_1,self.grid_location_2,self.grid_location_3]
        self.assertEqual(not_empty_grid_locations,expected_not_empty_grid_locations)
