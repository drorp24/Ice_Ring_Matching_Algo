from matching.matcher_input import MatcherInput

''' Reloading depo consists of 2 nodes:
arrive node & depart node so we can reset the cumulated travel_time between them.'''
NUM_OF_NODES_IN_RELOADING_DEPO = 2


class ORToolsReloader:
    def __init__(self, matcher_input: MatcherInput):
        self._matcher_input = matcher_input
        num_of_reloading_depo_nodes_per_formation = \
            self._matcher_input.config.reload_per_vehicle * NUM_OF_NODES_IN_RELOADING_DEPO
        num_of_reloading_depo_nodes = \
            self._matcher_input.delivering_drones_board.amount_of_formations() \
            * num_of_reloading_depo_nodes_per_formation
        self._reloading_virtual_depos_indices = list(range(
            len(self._matcher_input.graph.nodes),
            len(self._matcher_input.graph.nodes) + num_of_reloading_depo_nodes))
        self._arrive_indices = self._calc_reload_arriving_nodes()
        self._depart_indices = self._calc_reload_departing_nodes()
        self._num_of_nodes = len(self._matcher_input.graph.nodes) + len(self._reloading_virtual_depos_indices)
        self._reloading_depots_per_vehicle = {
            vehicle_index: depots
            for (vehicle_index, depots)
            in enumerate([self._reloading_virtual_depos_indices[
                          formation_index * num_of_reloading_depo_nodes_per_formation:
                          (formation_index + 1) * num_of_reloading_depo_nodes_per_formation]
                          for formation_index in range(
                    self._matcher_input.delivering_drones_board.amount_of_formations())])}
        self._vehicle_per_reloading_depot = {}
        for vehicle_index in self._reloading_depots_per_vehicle.keys():
            for depo in self._reloading_depots_per_vehicle[vehicle_index]:
                self._vehicle_per_reloading_depot[depo] = vehicle_index

    @property
    def num_of_nodes(self):
        return self._num_of_nodes

    @property
    def reloading_virtual_depos_indices(self):
        return self._reloading_virtual_depos_indices

    @property
    def arrive_indices(self):
        return self._arrive_indices

    @property
    def depart_indices(self):
        return self._depart_indices

    def get_reloading_depot_vehicle(self, depot_index) -> [int]:
        return self._vehicle_per_reloading_depot[depot_index]

    def get_vehicle_reloading_depots(self, vehicle_index) -> [int]:
        return self._reloading_depots_per_vehicle[vehicle_index]

    def get_vehicle_arrive_indices(self, vehicle_index) -> [int]:
        starting_index = 0
        return self._reloading_depots_per_vehicle[vehicle_index][starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def get_vehicle_depart_indices(self, vehicle_index) -> [int]:
        starting_index = 1
        return self._reloading_depots_per_vehicle[vehicle_index][starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def _calc_reload_arriving_nodes(self):
        starting_index = 0
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

    def _calc_reload_departing_nodes(self):
        starting_index = 1
        return self._reloading_virtual_depos_indices[starting_index::NUM_OF_NODES_IN_RELOADING_DEPO]

