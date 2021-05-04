from __future__ import annotations

import json
from copy import deepcopy, copy
from functools import lru_cache
from pathlib import Path

import numpy as np
from dataclasses import dataclass
from typing import List, Union
from networkx import DiGraph, subgraph, to_numpy_array, is_isomorphic
from networkx.readwrite import json_graph

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_id import EntityID
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
        return hash(tuple([self._internal]))

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        # noinspection PyArgumentList
        new_copy = OperationalNode(deepcopy(self._internal, memodict))
        memodict[id(self)] = new_copy
        return new_copy


@dataclass
class OperationalEdgeAttribs(JsonableBaseEntity):
    cost: float
    travel_time_min: float

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        return OperationalEdgeAttribs(cost=dict_input['cost'],
                                      travel_time_min=dict_input['travel_time_min'])

    def __hash__(self):
        return hash((self.cost, self.travel_time_min))


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
        return self.start_node.internal_node.id, self.end_node.internal_node.id, self.attributes.__dict__()

    def __hash__(self):
        return self.to_internal_tuple().__hash__()

    def __eq__(self, other: OperationalEdge):
        return self.start_node == other.start_node and \
               self.end_node == other.end_node and \
               self.attributes == other.attributes


class OperationalGraph(JsonableBaseEntity):

    def __init__(self):
        self._internal_graph = DiGraph()
        self._loading_docks_map = {}
        self._delivery_requests_map = {}

    def get_internal_graph(self):
        return self._internal_graph

    @property
    def nodes(self) -> List[OperationalNode]:
        nodes = []
        all_internal_nodes = self._get_all_internal_nodes_map()
        for id_ in list(self._internal_graph.nodes(data=False)):
            node = all_internal_nodes.get(id_, None)
            if node is None:
                raise RuntimeError(f"Graph index not found in node mapping")
            else:
                nodes.append(OperationalNode(node))
        return nodes

    @property
    def edges(self) -> List[OperationalEdge]:
        internal_edges = self._internal_graph.edges.data(data=True)
        all_internal_nodes = self._get_all_internal_nodes_map()
        return [OperationalEdge(OperationalNode(all_internal_nodes[edge[0]]),
                                OperationalNode(all_internal_nodes[edge[1]]),
                                OperationalEdgeAttribs(edge[2]['cost'], edge[2]['travel_time_min']))
                for edge in internal_edges]

    def calc_max_cost(self) -> float:
        return max(e.attributes.cost for e in self.edges[:])

    def calc_min_cost(self) -> float:
        return min(e.attributes.cost for e in self.edges[:])

    def calc_total_priority(self) -> int:
        return sum(n.get_priority() for n in self.nodes[:])

    def is_empty(self):
        return self._internal_graph.nodes.__len__() == 0

    def add_drone_loading_docks(self, drone_loading_docks: [DroneLoadingDock]):
        for dl in drone_loading_docks:
            self._loading_docks_map[dl.id] = dl
            self._internal_graph.add_node(dl.id)

    def add_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        for dr in delivery_requests:
            self._delivery_requests_map[dr.id] = dr
            self._internal_graph.add_node(dr.id)

    def add_operational_nodes(self, operational_nodes: [OperationalNode]):
        for operational_node in operational_nodes:
            if operational_node.internal_type is DeliveryRequest:
                self.add_delivery_requests([operational_node.internal_node])
            elif operational_node.internal_type is DroneLoadingDock:
                self.add_drone_loading_docks([operational_node.internal_node])
            else:
                raise TypeError(f"Not supported OperationalNode type: {operational_node.internal_type}")

    def add_operational_edges(self, operational_edges: [OperationalEdge]):
        self._internal_graph.add_edges_from(list(map(lambda oe: oe.to_internal_tuple(), operational_edges)))

    def calc_subgraph_in_time_window(self, time_window_scope: TimeWindowExtension) -> OperationalGraph:
        subgraph = OperationalGraph()
        nodes_at_time = []
        for node in self._get_all_internal_nodes_map().values():
            if node.time_window in time_window_scope:
                nodes_at_time.append(node.id)
                if type(node) is DeliveryRequest:
                    subgraph._delivery_requests_map[node.id] = node
                elif type(node) is DroneLoadingDock:
                    subgraph._loading_docks_map[node.id] = node
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_at_time)
        subgraph._internal_graph = extracted_subgraph
        return subgraph

    def calc_subgraph_below_priority(self, max_priority: int) -> OperationalGraph:
        subgraph = OperationalGraph()
        nodes_below_priority = []
        for node in self._get_all_internal_nodes_map().values():
            if node.priority < max_priority:
                nodes_below_priority.append(node.id)
                if type(node) is DeliveryRequest:
                    subgraph._delivery_requests_map[node.id] = node
                elif type(node) is DroneLoadingDock:
                    subgraph._loading_docks_map[node.id] = node
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_below_priority)
        subgraph._internal_graph = extracted_subgraph
        return subgraph

    def calc_subgraph_within_polygon(self, boundary: Polygon2D) -> OperationalGraph:
        subgraph = OperationalGraph()
        nodes_within_polygon = []
        for node in self._get_all_internal_nodes_map().values():
            if node.calc_location() in boundary:
                nodes_within_polygon.append(node.id)
                if type(node) is DeliveryRequest:
                    subgraph._delivery_requests_map[node.id] = node
                elif type(node) is DroneLoadingDock:
                    subgraph._loading_docks_map[node.id] = node
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(nodes_within_polygon)
        subgraph._internal_graph = extracted_subgraph
        return subgraph

    def create_subgraph_without_nodes(self, nodes_to_remove: [OperationalNode]):
        internal_nodes_to_remove = [node.internal_node for node in nodes_to_remove]
        subgraph = OperationalGraph()
        new_nodes = []
        for node in self._get_all_internal_nodes_map().values():
            if node not in internal_nodes_to_remove:
                new_nodes.append(node.id)
                if type(node) is DeliveryRequest:
                    subgraph._delivery_requests_map[node.id] = node
                elif type(node) is DroneLoadingDock:
                    subgraph._loading_docks_map[node.id] = node
        extracted_subgraph = self._extract_internal_subgraph_of_nodes(new_nodes)
        subgraph._internal_graph = extracted_subgraph
        return subgraph

    def to_cost_numpy_array(self, nonedge: float, dtype) -> np.ndarray:
        costs = to_numpy_array(self._internal_graph, weight="cost", nonedge=nonedge, dtype=dtype)
        if nonedge != 0:
            self._zero_nodes_travel_time_to_themselves(costs)
        return costs

    def to_travel_time_numpy_array(self, nonedge: float, dtype) -> np.ndarray:
        travel_times = to_numpy_array(self._internal_graph, weight="travel_time_min", nonedge=nonedge, dtype=dtype)
        if nonedge != 0:
            self._zero_nodes_travel_time_to_themselves(travel_times)
        return travel_times

    def get_node_index(self, node: OperationalNode) -> int:
        return self.nodes.index(node)

    def get_all_delivery_requests(self):
        return list(self._delivery_requests_map.values())

    def get_all_loading_docks(self):
        return list(self._loading_docks_map.values())

    def get_delivery_request(self, index: int):
        id_ = list(self._internal_graph.nodes(data=False))[index]
        return self._delivery_requests_map[id_]

    def get_loading_dock(self, index: int):
        id_ = list(self._internal_graph.nodes(data=False))[index]
        return self._loading_docks_map[id_]

    def get_node_index_by_id(self, id_: EntityID) -> int:
        index = list(self._internal_graph.nodes(data=False)).index(id_)
        return index

    @lru_cache()
    def get_nodes_indices_by_ids(self, ids: tuple(EntityID)) -> [int]:
        graph_ids = list(self._internal_graph.nodes(data=False))
        return [graph_ids.index(id_) for id_ in ids]

    def get_all_delivery_requests_indices(self) -> [int]:
        return self.get_nodes_indices_by_ids(tuple(self._delivery_requests_map.keys()))

    def get_all_loading_docks_indices(self) -> [int]:
        return self.get_nodes_indices_by_ids(tuple(self._loading_docks_map.keys()))

    def remove_delivery_requests(self, delivery_requests: [DeliveryRequest]):
        for dr in delivery_requests:
            self._delivery_requests_map.pop(dr.id)
            self._internal_graph.remove_node(dr.id)

    def remove_operational_nodes(self, operational_nodes: [OperationalNode]):
        self._internal_graph.remove_nodes_from(operational_nodes)

    def _zero_nodes_travel_time_to_themselves(self, travel_times: np.ndarray) -> None:
        for i in range(len(self._internal_graph.nodes)):
            travel_times[i, i] = 0

    def _extract_internal_subgraph_of_nodes(self, nodes_in_subgraph: [OperationalNode]) -> DiGraph:
        return DiGraph(self._internal_graph.subgraph(nodes_in_subgraph))

    def _get_all_internal_nodes_map(self):
        all_internal_nodes = copy(self._loading_docks_map)
        all_internal_nodes.update(self._delivery_requests_map)
        return all_internal_nodes

    def __hash__(self):
        return hash(self._internal_graph)

    def __repr__(self):
        return f"OperationalGraph: {self.__dict__()}"

    def __eq__(self, other):
        return all([is_isomorphic(self._internal_graph, other._internal_graph),
                    self._delivery_requests_map == other._delivery_requests_map,
                   self._loading_docks_map == other._loading_docks_map])

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        new_copy = OperationalGraph()
        new_copy._internal_graph = deepcopy(self._internal_graph)
        new_copy._loading_docks_map = deepcopy(self._loading_docks_map)
        new_copy._delivery_requests_map = deepcopy(self._delivery_requests_map)
        memodict[id(self)] = new_copy
        return new_copy

    def __dict__(self):
        d = {'__class__': type(self).__name__}
        d.update({"internal_graph": json_graph.node_link_data(self._internal_graph)})
        docks_map_dict = [dock.__dict__() for dock in list(self._loading_docks_map.values())]
        d.update({"loading_docks_map": docks_map_dict})
        requests_map_dict = [request.__dict__() for request in list(self._delivery_requests_map.values())]
        d.update({"delivery_requests_map": requests_map_dict})
        return d

    def __str__(self):
        return self.__repr__()

    @classmethod
    def dict_to_obj(cls, dict_input):
        assert (dict_input['__class__'] == cls.__name__)
        og = OperationalGraph()
        nodes = []
        graph_dict = dict_input['internal_graph']
        for node_dict in dict_input['internal_graph']['nodes']:
            if type(node_dict['id']) is EntityID:
                new_node_dict = {'id': node_dict['id']}
            else:
                new_node_dict = {'id': EntityID.dict_to_obj(node_dict['id'])}
            nodes.append(new_node_dict)
        graph_dict['nodes'] = nodes
        links = []
        for i, link_dict in enumerate(dict_input['internal_graph']['links']):
            new_link_dict = dict_input['internal_graph']['links'][i]
            if type(link_dict['source']) is EntityID:
                new_link_dict['source'] = link_dict['source']
                new_link_dict['target'] = link_dict['target']
            else:
                new_link_dict['source'] = EntityID.dict_to_obj(link_dict['source'])
                new_link_dict['target'] = EntityID.dict_to_obj(link_dict['target'])
            links.append(new_link_dict)
        graph_dict['links'] = links
        og._internal_graph = json_graph.node_link_graph(graph_dict)
        loading_docks = [DroneLoadingDock.dict_to_obj(dock)
                         for dock in dict_input['loading_docks_map']]
        og._loading_docks_map = {dock.id: dock for dock in loading_docks}
        delivery_requests = [DeliveryRequest.dict_to_obj(request)
                             for request in dict_input['delivery_requests_map']]
        og._delivery_requests_map = {request.id: request
                                     for request in delivery_requests}
        return og

    @staticmethod
    def encode_node(z):
        if isinstance(z, OperationalNode):
            return (z.__dict__())
        elif isinstance(z, EntityID):
            return (z.__dict__())
        else:
            type_name = z.__class__.__name__
            raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

    def to_json(self, file_path: Path):
        with open(file_path, 'w') as f:
            dict_self = self.__dict__()
            json.dump(dict_self, f, sort_keys=False, default=self.encode_node)


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
