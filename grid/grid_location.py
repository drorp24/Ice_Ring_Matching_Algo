from statistics import mean
from typing import List

from optional import Optional
from optional.abstract_optional import AbstractOptional
from optional.something import Something


class GridLocation(object):
    def __init__(self, row: int, column: int):
        self._row = row
        self._column = column

    @property
    def row(self) -> int:
        return self._row

    @property
    def column(self) -> int:
        return self._column

    def __add__(self, other):
        return GridLocation(self.row + other.row, self.column + other.column)

    def __sub__(self, other):
        return GridLocation(self.row - other.row, self.column - other.column)

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column

    def flatten(self):
        return [self._row, self._column]


class GridLocationServices:

    @staticmethod
    def get_not_empty_indices(grid_locations: [Optional.of(GridLocation)]) -> List[int]:
        return [index for index, grid_location in enumerate(grid_locations) if not grid_location.is_empty()]

    @staticmethod
    def get_not_empty_grid_locations(grid_locations: [Optional.of(GridLocation)]) -> List[GridLocation]:
        return list(map(Something.get, list(filter(AbstractOptional.is_present,grid_locations))))

    @staticmethod
    def calc_average(grid_locations: [Optional.of(GridLocation)]) -> Optional.of(GridLocation):
        filtered_grid_locations = GridLocationServices.get_not_empty_grid_locations(grid_locations)

        if not filtered_grid_locations:
            return Optional.empty()

        return Optional.of(GridLocation(
            *list(map(mean, zip(*list(grid_location.flatten() for grid_location in filtered_grid_locations))))))
