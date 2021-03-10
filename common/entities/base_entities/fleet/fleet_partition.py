from dataclasses import dataclass
from typing import Any, List

import numpy as np

from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from common.math.mip_solver import MIPData, MIPParameters, solve_mip


@dataclass
class FleetPartitionParameters:
    formation_drone_amount_options: [int]
    formation_type_probabilities: [float]
    fleet_drone_amount: int

    def get_amount_of_options(self) -> int:
        return len(self.formation_drone_amount_options)


@dataclass
class FormationTypeAmounts:
    amounts: {DroneFormationType, int}

    def get_formation_types(self) -> [DroneFormationType]:
        return list(self.amounts.keys())

    def get_drone_amounts(self) -> [int]:
        return [s.value for s in self.amounts.keys()]

    def get_formation_amounts(self) -> [int]:
        return list(self.amounts.values())

    def get_total_formation_amount(self) -> int:
        return int(sum(self.get_formation_amounts()))


class FleetPartition(object):

    def __init__(self, drone_set_properties: DroneSetProperties):
        self.fleet_partition_parameters: FleetPartitionParameters = FleetPartitionParameters([], [], 0)
        self.fleet_partition_parameters.fleet_drone_amount = drone_set_properties.drone_amount - \
                                                             FleetPartition.is_drone_amount_odd(drone_set_properties)
        formation_type_policy = drone_set_properties.drone_formation_policy.policy
        self.fleet_partition_parameters.formation_drone_amount_options = FleetPartition \
            .get_amount_of_drones_per_type_in_policy(formation_type_policy)
        self.fleet_partition_parameters.formation_type_probabilities = FleetPartition \
            .get_probs_per_type_in_policy(formation_type_policy)

    @staticmethod
    def is_drone_amount_odd(drone_set_properties):
        return drone_set_properties.drone_amount % 2 != 0

    @staticmethod
    def get_probs_per_type_in_policy(formation_type_policy):
        return list(formation_type_policy.values())

    @staticmethod
    def get_amount_of_drones_per_type_in_policy(formation_type_policy):
        return list(map(lambda ft: ft.get_amount_of_drones(), formation_type_policy.keys()))

    def _calc_number_variables(self) -> int:
        return self.fleet_partition_parameters.get_amount_of_options()

    @staticmethod
    def _export_from_mip_varaibles_formation_type_amounts(variables) -> FormationTypeAmounts:
        return FormationTypeAmounts({formation_type: variables[i].solution_value() for i, formation_type in
                                     enumerate(DroneFormationType)})

    def _has_zero_formation_type_probabilities(self):
        formation_type_probabilities = self.fleet_partition_parameters.formation_type_probabilities
        has_zero_probs = any(map(lambda prob: prob == 0, formation_type_probabilities))
        return has_zero_probs

    def _has_all_zero_formation_type_probabilities(self):
        formation_type_probabilities = self.fleet_partition_parameters.formation_type_probabilities
        has_zero_probs = all(map(lambda prob: prob == 0, formation_type_probabilities))
        return has_zero_probs

    def _calc_objective_coefficients(self) -> Any:
        assert not self._has_all_zero_formation_type_probabilities()
        # --- standard problem formulation
        if not self._has_zero_formation_type_probabilities():
            return self._calc_objective_coefficients_given_all_positive_probabilities()
        # --- problem formulation given zero probability values, while still optimizing for max overall usage
        return self._calc_objective_coefficients_given_zero_probabilities()

    def _calc_objective_coefficients_given_all_positive_probabilities(self):
        # In the standard formulation, when all probabilities are positive the objective coefficients should all be 1.
        # we then try to minimize the amount of formations created in the fleet, equally for each formation type
        num_vars = self._calc_number_variables()
        return np.ones(num_vars).tolist()

    def _calc_objective_coefficients_given_zero_probabilities(self):
        # In the partially zero formulation, when zero probabilities exists, we make non-zero probabilities zero. This
        # is done in order to minimize the useage of the "unwanted" formation types.
        num_vars = self._calc_number_variables()
        non_zero_indices = self._calc_non_zero_indices(self.fleet_partition_parameters.formation_type_probabilities)
        objective_coefficients = np.ones(num_vars)
        objective_coefficients[non_zero_indices] = 0
        return objective_coefficients.tolist()

    def _calc_inequality_constraints_coefficients(self) -> Any:
        assert not self._has_all_zero_formation_type_probabilities()
        # --- standard problem formulation
        if not self._has_zero_formation_type_probabilities():
            return self._calc_inequality_constraints_coefficients_given_all_positive_probabilities()
        # --- problem formulation given zero probability values, while still optimizing for max overall usage
        return self._calc_inequality_constraints_coefficients_given_zero_probabilities()

    def _calc_inequality_constraints_coefficients_given_all_positive_probabilities(self):
        formation_type_probabilities = self.normalize_probabilities(
            self.fleet_partition_parameters.formation_type_probabilities)
        return self._calc_constraints_matrix(formation_type_probabilities)

    def _calc_inequality_constraints_coefficients_given_zero_probabilities(self):
        formation_type_probabilities = self.fleet_partition_parameters.formation_type_probabilities
        non_zero_indices = self._calc_non_zero_indices(formation_type_probabilities)
        if any(non_zero_indices):
            formation_type_probabilities = self.normalize_probabilities(formation_type_probabilities)
        return self._calc_constraints_matrix(formation_type_probabilities)

    def _calc_constraints_matrix(self, formation_type_probabilities):
        num_vars = self._calc_number_variables()
        constraints_matrix = np.zeros((1, num_vars))
        for i in range(0, num_vars):
            constraints_matrix[0, i] = formation_type_probabilities[i]
        # --- given zero indices, we multiply the first non zero index by -1
        non_zero_indices = self._calc_non_zero_indices(formation_type_probabilities)
        constraints_matrix[0, non_zero_indices[0]] = -1 * constraints_matrix[0, non_zero_indices[0]]
        return constraints_matrix.tolist()

    @staticmethod
    def normalize_probabilities(formation_type_probabilities):
        return [prob / sum(formation_type_probabilities) for prob in formation_type_probabilities]

    @staticmethod
    def _calc_non_zero_indices(formation_type_probabilities):
        return [i for i, e in enumerate(formation_type_probabilities) if e != 0]

    def _calc_equality_constraints_coefficients(self) -> List[List[int]]:
        return [self.fleet_partition_parameters.formation_drone_amount_options]

    def _calc_equality_bounds(self) -> List:
        return [self.fleet_partition_parameters.fleet_drone_amount]

    @staticmethod
    def _calc_inequality_bounds() -> List:
        # This is const. zero due to the problem formulation
        return [0]

    def _formulate_fleet_partition_as_mip(self) -> MIPData:
        data = {MIPParameters.num_variables: self._calc_number_variables(),
                MIPParameters.equality_constraints_coefficients: self._calc_equality_constraints_coefficients(),
                MIPParameters.inequality_constraints_coefficients: self._calc_inequality_constraints_coefficients(),
                MIPParameters.inequality_bounds: self._calc_inequality_bounds(),
                MIPParameters.equality_bounds: self._calc_equality_bounds(),
                MIPParameters.objective_coefficients: self._calc_objective_coefficients()}
        return MIPData(data)

    def solve(self) -> FormationTypeAmounts:
        mip_data = self._formulate_fleet_partition_as_mip()
        variables = solve_mip(mip_data)
        return self._export_from_mip_varaibles_formation_type_amounts(variables=variables)
