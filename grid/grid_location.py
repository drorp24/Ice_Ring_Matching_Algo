from typing import List

import numpy as np


# class BaseGridLocation(ABC):
#
#     @abstractmethod
#     def __add__(self, other):
#         raise NotImplementedError()
#
#     @abstractmethod
#     def __sub__(self, other):
#         raise NotImplementedError()


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

    def as_list(self):
        return [self._row, self._column]


# class NoneGridLocation(BaseGridLocation):
#     def __init__(self):
#         super().__init__(None, None)
#
#     def __add__(self, other):
#         return self
#
#     def __sub__(self, other):
#         return self


class GridLocationServices:
    @staticmethod
    def calc_average(grid_locations: List[GridLocation]) -> GridLocation:
        return GridLocation(
            *list(map(np.mean, zip(*list(grid_location.as_list() for grid_location in grid_locations)))))