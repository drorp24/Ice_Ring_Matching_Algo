from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

from networkx import DiGraph, subgraph

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.temporal import TimeWindowExtension, Temporal
from common.utils.class_controller import name_to_class, get_all_module_class_names_from_globals
from geometry.geo2d import Polygon2D
from geometry.utils import Localizable


class OperationalNode(JsonableBaseEntity):

    def __init__(self, internal_node: Union[DeliveryRequest, DroneLoadingDock]):
        assert_node_is_localizable(internal_node)
        assert_node_is_temporal(internal_node)
        self._internal = internal_node

    @property
    def internal_node(self) -> Union[DeliveryRequest, DroneLoadingDock]:
        return self._internal

    @property
    def internal_type(self):
        return type(self.internal_node)

    def get_priority(self) -> int:
        return self.internal_node.priority

    def get_time_window(self) -> TimeWindowExtension:
        return self.internal_node.time_window

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        module_location = __name__
        internal_class_name = dict_input['internal_node']['__class__']
        assert (internal_class_name in get_all_module_class_names_from_globals(globals()))
        return OperationalNode(name_to_class(internal_class_name, module_location)
                               .dict_to_obj(dict_input['internal_node']))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.internal_node == other.internal_node

    def __hash__(self):
        return hash(self._internal)


@dataclass
class OperationalEdgeAttribs(JsonableBaseEntity):

    def __init__(self, cost: int):
        self._cost = cost

    @property
    def cost(self):
        return self._cost

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return OperationalEdgeAttribs(dict_input['cost'])

    def __eq__(self, other: OperationalEdgeAttribs):
        return self.cost == other.cost

    def __hash__(self):
        return hash(self._cost)


class OperationalEdge(JsonableBaseEntity):

    def __init__(self, start_node: OperationalNode, end_node: OperationalNode, attributes: OperationalEdgeAttribs):
        self._start_node = start_node
        self._end_node = end_node
        self._attributes = attributes

    @property
    def start_node(self):
        return self._start_node

    @property
    def end_node(self):
        return self._end_node

    @property
    def attributes(self):
        return self._attributes

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return OperationalEdge(start_node=OperationalNode.dict_to_obj(dict_input['start_node']),
                               end_node=OperationalNode.dict_to_obj(dict_input['end_node']),
                               attributes=OperationalEdgeAttribs.dict_to_obj(dict_input['attributes']))

    def to_internal_tuple(self):
        return self.start_node, self.end_node, self.attributes.__dict__()

    def __hash__(self):
        return self.to_internal_tuple().__hash__()

    def __eq__(self, other: OperationalEdge):
        return self.start_node == other.start_node and \
               self.end_node == other.end_node and \
               self.attributes == other.attributes


class OperationalGraph(JsonableBaseEntity):

    def __init__(self):
        self._internal_graph = DiGraph()

    def get_internal_graph(self):
        return self._internal_graph

    @property
    def nodes(self) -> List[OperationalNode]:
        return list(self._internal_graph.nodes(data=False))

    @property
    def edges(self) -> List[OperationalEdge]:
        internal_edges = self._internal_graph.edges.data(data=True)
        return [OperationalEdge(edge[0], edge[1], OperationalEdgeAttribs(edge[2]['cost'])) for edge in internal_edges]

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        og = OperationalGraph()
        og.add_operational_nodes([OperationalNode.dict_to_obj(node) for node in dict_input['nodes']])
        og.add_operational_edges([OperationalEdge.dict_to_obj(edge) for edge in dict_input['edges']])
        return og

    def is_empty(self):
        return self._internal_graph.nodes.__len__() == 0

    def set_internal_graph(self, networkx_graph: DiGraph):
        self._internal_graph = networkx_graph

    def add_drone_loading_docks(self, drone_loading_docks: [DroneLoadingDock]):
        self.add_operational_nodes([OperationalNode(dl) for dl in drone_loading_docks])

    def add_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        self.add_operational_nodes([OperationalNode(dr) for dr in delivery_requests])

    def add_operational_nodes(self, operational_nodes: [OperationalNode]):
        self._internal_graph.add_nodes_from(operational_nodes)

    def add_operational_edges(self, operational_edges: [OperationalEdge]):
        self._internal_graph.add_edges_from(list(map(lambda oe: oe.to_internal_tuple(), operational_edges)))

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindowExtension) -> OperationalGraph:
        nodes_at_time = [node for node in self.nodes if node.get_time_window() in time_window_scope]
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_at_time)
        return OperationalGraph._create_from_extracted_subgraph(extracted_subgraph)

    def calc_subgraph_below_priority(self, max_priority: int) -> OperationalGraph:
        nodes_below_priority = [node for node in self.nodes if node.get_priority() < max_priority]
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_below_priority)
        return OperationalGraph._create_from_extracted_subgraph(extracted_subgraph)

    def calc_subgraph_within_polygon(self, boundary: Polygon2D) -> OperationalGraph:
        nodes_within_polygon = [node for node in self.nodes if node.internal_node.calc_location() in boundary]
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_within_polygon)
        return OperationalGraph._create_from_extracted_subgraph(extracted_subgraph)

    def _extract_internal_subgraph_of_nodes(self, nodes_in_subgraph: [OperationalNode]) -> DiGraph:
        return DiGraph(self._internal_graph.subgraph(nodes_in_subgraph))

    @staticmethod
    def _create_from_extracted_subgraph(extracted_subgraph: subgraph):
        internal_subgraph = OperationalGraph()
        internal_subgraph.set_internal_graph(extracted_subgraph)
        return internal_subgraph

    def __hash__(self):
        return hash(self._internal_graph)

    def __eq__(self, other):
        return self.nodes == other.nodes and self.edges == other.edges


def assert_node_is_temporal(internal_node) -> None:
    if not issubclass(type(internal_node), Temporal):
        raise NonTemporalNodeException()


def assert_node_is_localizable(internal_node) -> None:
    if not issubclass(type(internal_node), Localizable):
        raise NonLocalizableNodeException()


class NonLocalizableNodeException(Exception):
    pass


class NonTemporalNodeException(Exception):
    pass
