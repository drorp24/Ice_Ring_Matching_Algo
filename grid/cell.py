from attr import dataclass

from grid.cell_data import CellData, EnvelopeCellData


@dataclass
class Location:
    row: int
    column: int


@dataclass
class Cell:
    location: Location
    data: CellData


class EnvelopeCell(Cell):
    def __init__(self, location: Location, data: EnvelopeCellData):
        super.__init__(location, data)
