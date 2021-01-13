from dataclasses import dataclass
from typing import Any

import numpy as np

from common.entities.base_entities.drone import DroneType
from common.entities.base_entities.drone_formation import DroneFormationType, DroneFormation, DroneFormationOptions, \
    DroneFormations
from common.entities.base_entities.fleet.fleet_partition import FormationTypeAmounts
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
from common.math.mip_solver import MIPSolver, MIPData, MIPParameters


@dataclass
class ConfigurationAttributionParameters:
    fleet_size: int
    total_formation_size: int
    drone_type: DroneType

    formation_types: [DroneFormationType]
    formation_sizes: [int]
    formation_amounts: [int]

    configurations: []
    configuration_options_size: int
    configurations_probabilities: [float]


@dataclass
class DroneFormationsPerTypeAmounts:
    amounts: {DroneFormation, int}


class FleetConfigurationAttribution:
    attribution_config: ConfigurationAttributionParameters = \
        ConfigurationAttributionParameters(0, 0, DroneType.drone_type_1, [], [], [], [], 0, [])

    @classmethod
    def extract_parameters(cls, formation_type_amounts: FormationTypeAmounts,
                           drone_set_properties: DroneSetProperties):
        cls.attribution_config.fleet_size = drone_set_properties.drone_amount
        cls.attribution_config.drone_type = drone_set_properties.drone_type

        cls.attribution_config.formation_types = formation_type_amounts.get_formation_types()
        cls.attribution_config.formation_sizes = formation_type_amounts.get_drone_amounts()
        cls.attribution_config.formation_amounts = formation_type_amounts.get_formation_amounts()
        cls.attribution_config.total_formation_size = formation_type_amounts.get_total_formation_amount()

        policy = drone_set_properties.package_configuration_policy
        cls.attribution_config.configuration_options_size = policy.get_amount()
        cls.attribution_config.configurations = policy.get_configurations()
        cls.attribution_config.configurations_probabilities = policy.get_probabilities()

    @staticmethod
    def _calc_formation_amounts_intervals(formation_amounts):
        return [range(int(sum(formation_amounts[0:i])), int(sum(formation_amounts[0:i + 1])))
                for i in range(len(formation_amounts))]

    @classmethod
    def _calc_number_variables(cls) -> int:
        return int(sum(cls.attribution_config.formation_amounts) *
                   cls.attribution_config.configuration_options_size)

    @classmethod
    def _calc_configuration_options_constraints(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.attribution_config.configuration_options_size
        total_formation_size = cls.attribution_config.total_formation_size
        constraints_coefficients = np.zeros((total_formation_size, num_vars))
        for i in range(total_formation_size):
            constraints_coefficients[i, i * configuration_options_size: (i + 1) * configuration_options_size] = 1
        return constraints_coefficients.tolist()

    @classmethod
    def _calc_configuration_options_bounds(cls) -> Any:
        total_formation_size = cls.attribution_config.total_formation_size
        bounds = np.ones(total_formation_size)
        return bounds.tolist()

    @classmethod
    def _calc_configuration_policy_constraints(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.attribution_config.configuration_options_size
        formation_amounts = cls.attribution_config.formation_amounts
        formation_sizes = cls.attribution_config.formation_sizes
        return FleetConfigurationAttribution._calc_constraints_coefficients(configuration_options_size,
                                                                            formation_amounts,
                                                                            formation_sizes,
                                                                            num_vars)

    @staticmethod
    def _calc_constraints_coefficients(configuration_options_size, formation_amounts, formation_sizes, num_vars):
        constraints_coefficients = np.zeros((configuration_options_size, num_vars))
        for i in range(configuration_options_size):
            for j in range(len(formation_amounts) - 1):
                constraints_coefficients[i, i: int(formation_amounts[j] * configuration_options_size):configuration_options_size] = formation_sizes[j]
                constraints_coefficients[i, i + int(formation_amounts[j] * configuration_options_size)::configuration_options_size] = formation_sizes[j + 1]
        return constraints_coefficients.tolist()

    @classmethod
    def _calc_configuration_policy_bounds(cls) -> [float]:
        weights = cls.attribution_config.configurations_probabilities
        fleet_size = cls.attribution_config.fleet_size
        bounds = [weight * fleet_size for weight in weights]
        return bounds

    @classmethod
    def _calc_objective_coefficients(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.attribution_config.configuration_options_size
        formation_amounts = cls.attribution_config.formation_amounts
        formation_sizes = cls.attribution_config.formation_sizes
        constraints_coefficients = np.zeros(num_vars)
        for i in range(len(formation_amounts)):
            constraints_coefficients[int(i * formation_amounts[i] * configuration_options_size):
                                     int((i + 1) * formation_amounts[i] * configuration_options_size)] = \
                formation_sizes[i]
        return constraints_coefficients.tolist()

    @classmethod
    def _formulate_as_mip_problem(cls) -> MIPData:
        data = {MIPParameters.num_variables: cls._calc_number_variables(),
                MIPParameters.inequality_constraints_coefficients:
                    cls._calc_configuration_policy_constraints() + cls._calc_configuration_options_constraints(),
                MIPParameters.inequality_bounds:
                    cls._calc_configuration_policy_bounds() + cls._calc_configuration_options_bounds(),
                MIPParameters.objective_coefficients: cls._calc_objective_coefficients()}
        return MIPData(data)

    @classmethod
    def _get_formation_size_type(cls, index: int) -> DroneFormationType:
        intervals = cls._calc_formation_amounts_intervals(cls.attribution_config.formation_amounts)
        for interval in intervals:
            if index in interval:
                formation_size_idx = intervals.index(interval)
                return cls.attribution_config.formation_types[formation_size_idx]

    @classmethod
    def _export_drone_formation_amounts(cls, variables) -> DroneFormationsPerTypeAmounts:
        formation_amounts = DroneFormations.create_default_drone_formations_amounts(
            cls.attribution_config.drone_type)
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.attribution_config.configuration_options_size
        platform_type = cls.attribution_config.drone_type
        variables = [variables[j].solution_value() for j in range(num_vars)]
        chosen_formations_indices = [i % configuration_options_size for i, x in enumerate(variables) if x == 1.0]
        for i in range(len(chosen_formations_indices)):
            formation_size = cls._get_formation_size_type(i)
            configuration = cls.attribution_config.configurations[chosen_formations_indices[i]]
            formation_option = DroneFormationOptions.get_formation_option(configuration, platform_type)
            drone_formation = DroneFormations.get_drone_formation(formation_size, formation_option, platform_type)
            formation_amounts[drone_formation] += 1
        return DroneFormationsPerTypeAmounts(formation_amounts)

    @classmethod
    def solve(cls) -> DroneFormationsPerTypeAmounts:
        mip_data = cls._formulate_as_mip_problem()
        variables = MIPSolver.set_variables(parameters=mip_data)
        mip_solver = MIPSolver()
        mip_solver.set_inequalities_constraints(parameters=mip_data, variables=variables)
        mip_solver.set_objective_coeffs(parameters=mip_data, variables=variables)
        mip_solver.set_maximization()
        mip_solver.solve()
        return cls._export_drone_formation_amounts(variables)
