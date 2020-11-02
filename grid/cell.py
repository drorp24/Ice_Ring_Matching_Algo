from attr import dataclass

from grid.cell_data import CellData, EnvelopeCellData


@dataclass
class GridLocation:
    row: int
    column: int


@dataclass
class Cell:
    location: GridLocation
    data: CellData


class EnvelopeCell(Cell):
    def __init__(self, grid_location: GridLocation, data: EnvelopeCellData):
        super.__init__(grid_location, data)
