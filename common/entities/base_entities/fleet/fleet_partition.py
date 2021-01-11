from dataclasses import dataclass
from typing import Any, List

import numpy as np

from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from common.math.mip_solver import MIPSolver, MIPData, MIPParameters


@dataclass
class FleetPartitionParameters:
    formation_drone_amount_options: [int]
    formation_type_probabilities: [float]
    fleet_drone_amount: int

    def amount_of_options(self) -> int:
        return len(self.formation_drone_amount_options)


@dataclass
class FormationTypeAmounts:
    amounts: {DroneFormationType, int}


class FleetPartition(object):
    fleet_partition_parameters: FleetPartitionParameters = FleetPartitionParameters([], [], 0)

    @classmethod
    def extract_parameters(cls, drone_set_properties: DroneSetProperties):
        cls.fleet_partition_parameters.fleet_drone_amount = drone_set_properties.drone_amount
        formation_type_policy = drone_set_properties.drone_formation_policy.formation_type_policy
        cls.fleet_partition_parameters.formation_drone_amount_options = FleetPartition \
            .get_amount_of_drones_per_type_in_policy(formation_type_policy)
        cls.fleet_partition_parameters.formation_type_probabilities = FleetPartition \
            .get_probs_per_type_in_policy(formation_type_policy)

    @classmethod
    def get_probs_per_type_in_policy(cls, formation_type_policy):
        min_prob_epsilon = 0.0
        return [min(max(a, min_prob_epsilon), 1 - min_prob_epsilon) for a in list(formation_type_policy.values())]

    @classmethod
    def get_amount_of_drones_per_type_in_policy(cls, formation_type_policy):
        return list(map(lambda ft: ft.get_amount_of_drones(), formation_type_policy.keys()))

    @classmethod
    def _calc_number_variables(cls) -> int:
        return cls.fleet_partition_parameters.amount_of_options()

    @classmethod
    def _export_formation_amounts(cls, variables) -> FormationTypeAmounts:
        return FormationTypeAmounts({formation_type: variables[i].solution_value() for i, formation_type in
                                     enumerate(DroneFormationType)})

    @classmethod
    def _calc_objective_coefficients(cls) -> Any:
        formation_type_probabilities = cls.fleet_partition_parameters.formation_type_probabilities
        non_zero_indices = [i for i, e in enumerate(formation_type_probabilities) if e != 0]
        num_vars = cls._calc_number_variables()
        objective_coefficients = np.ones(num_vars)
        if num_vars != len(non_zero_indices):
            objective_coefficients[non_zero_indices] = 0
        b = objective_coefficients.tolist()
        return b
        # return np.ones(num_vars).tolist()

    @classmethod
    def _calc_inequality_constraints_coefficients(cls) -> Any:
        formation_type_probabilities = cls.fleet_partition_parameters.formation_type_probabilities
        non_zero_indices = [i for i, e in enumerate(formation_type_probabilities) if e != 0]
        num_vars = cls._calc_number_variables()
        constraints_matrix = np.zeros((1, num_vars))
        if any(non_zero_indices):
            s = sum([formation_type_probabilities[ind] for ind in non_zero_indices])
            formation_type_probabilities = [prob / s for prob in formation_type_probabilities]
        for i in range(num_vars):
            if i != non_zero_indices[0]:
                constraints_matrix[0, i] = formation_type_probabilities[i]
            else:
                constraints_matrix[0, i] = -1 * formation_type_probabilities[i]
        # for i in range(num_vars):
        #     constraints_matrix[0, i] = formation_type_probabilities[i]
        return constraints_matrix.tolist()

    @classmethod
    def _calc_equality_constraints_coefficients(cls) -> List[List[int]]:
        return [cls.fleet_partition_parameters.formation_drone_amount_options]

    @classmethod
    def _calc_equality_bounds(cls) -> List:
        return [cls.fleet_partition_parameters.fleet_drone_amount]

    @classmethod
    def _calc_inequality_bounds(cls) -> List:
        return [0]

    @classmethod
    def _formulate_as_mip_problem(cls) -> MIPData:
        data = {MIPParameters.num_variables: cls._calc_number_variables(),
                MIPParameters.equality_constraints_coefficients: cls._calc_equality_constraints_coefficients(),
                MIPParameters.inequality_constraints_coefficients: cls._calc_inequality_constraints_coefficients(),
                MIPParameters.inequality_bounds: cls._calc_inequality_bounds(),
                MIPParameters.equality_bounds: cls._calc_equality_bounds(),
                MIPParameters.objective_coefficients: cls._calc_objective_coefficients()}
        return MIPData(data)

    @classmethod
    def solve(cls) -> FormationTypeAmounts:
        mip_data = cls._formulate_as_mip_problem()
        mip_solver = MIPSolver()
        variables = mip_solver.set_variables(parameters=mip_data)
        mip_solver.set_equalities_constraints(parameters=mip_data, variables=variables)
        mip_solver.set_inequalities_constraints(parameters=mip_data, variables=variables)
        mip_solver.set_objective_coeffs(parameters=mip_data, variables=variables)
        mip_solver.set_minimization()
        mip_solver.solve()
        return cls._export_formation_amounts(variables=variables)
