import unittest

from common.math.angle import Angle, AngleUnit
from grid.cell import EnvelopeCell, GridLocation, CellServices


class BasicCellServiceTestCase(unittest.TestCase):

    def test_cell_service_commutative(self):
        cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        cell2 = EnvelopeCell(GridLocation(2, 3), Angle(15, AngleUnit.DEGREE))
        dist12 = CellServices.get_distance(cell1, cell2)
        dist21 = CellServices.get_distance(cell2, cell1)
        self.assertEqual(dist12, dist21)

    def test_cell_service_angle(self):
        cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        cell2 = EnvelopeCell(GridLocation(0, 0), Angle(15, AngleUnit.DEGREE))
        cell3 = EnvelopeCell(GridLocation(0, 0), Angle(30, AngleUnit.DEGREE))
        dist12 = CellServices.get_distance(cell1, cell2)
        dist13 = CellServices.get_distance(cell1, cell3)
        dist23 = CellServices.get_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)

    def test_cell_service_grid_location(self):
        cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        cell2 = EnvelopeCell(GridLocation(1, 1), Angle(0, AngleUnit.DEGREE))
        cell3 = EnvelopeCell(GridLocation(2, 2), Angle(0, AngleUnit.DEGREE))
        dist12 = CellServices.get_distance(cell1, cell2)
        dist13 = CellServices.get_distance(cell1, cell3)
        dist23 = CellServices.get_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)

    def test_cell_service_angle_delta_cost(self):
        cell1 = EnvelopeCell(GridLocation(0, 0), Angle(0, AngleUnit.DEGREE))
        cell2 = EnvelopeCell(GridLocation(1, 1), Angle(0, AngleUnit.DEGREE))
        cell3 = EnvelopeCell(GridLocation(2, 2), Angle(0, AngleUnit.DEGREE))
        dist12 = CellServices.get_distance(cell1, cell2)
        dist13 = CellServices.get_distance(cell1, cell3)
        dist23 = CellServices.get_distance(cell2, cell3)

        self.assertEqual(dist12, dist23)
        self.assertGreater(dist13, dist12)
