from typing import List

import numpy as np
from optional import Optional


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
        if not isinstance(other, GridLocation):
            return self

        return GridLocation(self.row + other.row, self.column + other.column)

    def __sub__(self, other):
        if not isinstance(other, GridLocation):
            return self

        return GridLocation(self.row - other.row, self.column - other.column)

    def __eq__(self, other):
        if not isinstance(other, GridLocation):
            return False

        return self.row == other.row and self.column == other.column

    def flatten(self):
        return [self._row, self._column]


class GridLocationServices:

    @staticmethod
    def get_not_empty_indices(grid_locations: [Optional.of(GridLocation)]) -> List[int]:
        return [index for index, grid_location in enumerate(grid_locations) if not grid_location.is_empty()]

    @staticmethod
    def get_not_empty_grid_locations(grid_locations: [Optional.of(GridLocation)]) -> List[GridLocation]:
        filtered_grid_indices = list(
            map(grid_locations.__getitem__, GridLocationServices.get_not_empty_indices(grid_locations)))
        return [grid_location.get() for grid_location in filtered_grid_indices]

    @staticmethod
    def calc_average(grid_locations: [Optional.of(GridLocation)]) -> GridLocation:
        filtered_grid_locations = GridLocationServices.get_not_empty_grid_locations(grid_locations)
        return GridLocation(
            *list(map(np.mean, zip(*list(grid_location.flatten() for grid_location in filtered_grid_locations)))))
