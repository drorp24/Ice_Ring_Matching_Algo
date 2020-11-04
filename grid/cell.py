from attr import dataclass

from grid.cell_data import CellData, EnvelopeCellData


@dataclass
class GridLocation:
    row: int
    column: int


@dataclass
class NoneGridLocation(GridLocation):
    row: int = None
    column: int = None


@dataclass
class Cell:
    location: GridLocation
    data: CellData


@dataclass
class EnvelopeCell(Cell):
    location: EnvelopeCellData
    data: CellData
