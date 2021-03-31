from functools import lru_cache

from ortools.constraint_solver.pywrapcp import RoutingIndexManager


class OrToolsIndexManagerWrapper:
    def __init__(self, index_manager: RoutingIndexManager):
        self._index_manager = index_manager

    def get_internal(self) -> RoutingIndexManager:
        return self._index_manager

    def get_number_of_nodes(self) -> int:
        return self._index_manager.GetNumberOfNodes()

    def get_number_of_vehicles(self) -> int:
        return self._index_manager.GetNumberOfVehicles()

    def get_number_of_indices(self) -> int:
        return self._index_manager.GetNumberOfIndices()

    @lru_cache()
    def node_to_index(self, node: int) -> int:
        return self._index_manager.NodeToIndex(node)

    @lru_cache()
    def index_to_node(self, index: int) -> int:
        return self._index_manager.IndexToNode(index)
