from dataclasses import dataclass
from typing import Any

import numpy as np

from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from common.math.mip_solver import MIPSolver, MIPData, MIPParameters


@dataclass
class FleetPartitionParameters:
    formation_type_options: [int]
    formation_type_probabilities: [float]
    fleet_drone_amount: int

    def amount_of_options(self) -> int:
        return len(self.formation_type_options)


@dataclass
class FormationTypeAmounts:
    amounts: {DroneFormationType, int}


class FleetPartition(object):
    fleet_partition_parameters: FleetPartitionParameters = FleetPartitionParameters([], [], 0)

    @classmethod
    def extract_parameters(cls, drone_set_properties: DroneSetProperties):
        cls.fleet_partition_parameters.fleet_drone_amount = drone_set_properties.drone_amount
        formation_type_policy = drone_set_properties.drone_formation_policy.formation_type_policy
        cls.fleet_partition_parameters.formation_type_options = FleetPartition \
            .get_amount_of_drones_per_type_in_policy(formation_type_policy)
        cls.fleet_partition_parameters.formation_type_probabilities = FleetPartition \
            .get_probs_per_type_in_policy(formation_type_policy)

    @classmethod
    def get_probs_per_type_in_policy(cls, formation_type_policy):
        return list(formation_type_policy.values())

    @classmethod
    def get_amount_of_drones_per_type_in_policy(cls, formation_type_policy):
        return list(map(lambda ft: ft.get_amount_of_drones(), formation_type_policy.keys()))

    @classmethod
    def _calc_number_variables(cls) -> int:
        return cls.fleet_partition_parameters.amount_of_options()

    @classmethod
    def _export_formation_amounts(cls, variables) -> FormationTypeAmounts:
        formation_amounts = {formation_type: variables[i].solution_value() for i, formation_type in
                             enumerate(DroneFormationType)}
        return FormationTypeAmounts(formation_amounts)

    @classmethod
    def _calc_objective_coefficients(cls) -> Any:
        formation_size_distribution = cls.fleet_partition_parameters.formation_type_probabilities
        non_zero_indices = [i for i, e in enumerate(formation_size_distribution) if e != 0]
        num_vars = cls._calc_number_variables()
        objective_coefficients = np.ones(num_vars)
        if num_vars == len(non_zero_indices):
            return objective_coefficients.tolist()
        objective_coefficients[non_zero_indices] = 0
        return objective_coefficients.tolist()

    @classmethod
    def _calc_inequality_constraints_coefficients(cls) -> Any:
        formation_size_distribution = cls.fleet_partition_parameters.formation_type_probabilities
        non_zero_indices = [i for i, e in enumerate(formation_size_distribution) if e != 0]
        num_vars = cls._calc_number_variables()
        constraints_matrix = np.zeros((1, num_vars))
        if any(non_zero_indices):
            formation_size_distribution = [prob / formation_size_distribution[non_zero_indices[0]]
                                           for prob in formation_size_distribution]
        for i in range(num_vars):
            if i != non_zero_indices[0]:
                constraints_matrix[0, i] = formation_size_distribution[i]
            else:
                constraints_matrix[0, i] = -1 * formation_size_distribution[i]
        return constraints_matrix.tolist()

    @classmethod
    def _calc_equality_constraints_coefficients(cls) -> Any:
        num_vars = cls._calc_number_variables()
        constraints_matrix = np.zeros((1, num_vars))
        for i in range(num_vars):
            constraints_matrix[0, i] = cls.fleet_partition_parameters.formation_type_options[i]
        return constraints_matrix.tolist()

    @classmethod
    def _calc_equality_bounds(cls) -> Any:
        bounds = np.zeros(1)
        bounds[0] = cls.fleet_partition_parameters.fleet_drone_amount
        return bounds.tolist()

    @classmethod
    def _calc_inequality_bounds(cls) -> Any:
        bounds = np.zeros(1)
        return bounds.tolist()

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
