from dataclasses import dataclass
from typing import Any

import numpy as np

from common.entities.drone import PlatformType
from common.entities.drone_formation import FormationSize, DroneFormation, DroneFormationOptions, DroneFormations
from common.tools.fleet_partition import FormationSizesAmounts
from common.tools.fleet_property_sets import PlatformPropertySet
from common.tools.mip_solver import MIPSolver, MIPData, MIPParameters


@dataclass
class ConfigurationAttributionParameters:
    formation_sizes: [int]
    formation_amounts: [int]
    configurations_policy: [float]
    fleet_size: int
    configuration_options_size: int
    total_formation_size: int
    platform_type: PlatformType
    formation_size_type: [FormationSize]
    configurations: []
    formation_amounts_intervals: []


@dataclass
class DroneFormationsPerTypeAmounts:
    amounts: {DroneFormation, int}


class FleetConfigurationAttribution:
    configuration_attribution_parameters: ConfigurationAttributionParameters = \
        ConfigurationAttributionParameters([], [], [], 0, 0, 0, PlatformType.platform_1, [], [], [])

    @classmethod
    def extract_parameters(cls, formation_sizes_amounts: FormationSizesAmounts,
                           platform_property_set: PlatformPropertySet):
        cls.configuration_attribution_parameters.fleet_size = platform_property_set.size
        cls.configuration_attribution_parameters.formation_amounts = list(formation_sizes_amounts.amounts.values())
        cls.configuration_attribution_parameters.formation_size_type = list(formation_sizes_amounts.amounts.keys())
        cls.configuration_attribution_parameters.formation_sizes = [
            s.value for s in formation_sizes_amounts.amounts.keys()]
        cls.configuration_attribution_parameters.configurations = list(
            platform_property_set.configuration_policy.configurations_policy.keys())
        cls.configuration_attribution_parameters.configuration_options_size = len(
            platform_property_set.configuration_policy.configurations_policy)
        cls.configuration_attribution_parameters.configurations = list(
            platform_property_set.configuration_policy.configurations_policy.keys())
        cls.configuration_attribution_parameters.configurations_policy = list(
            platform_property_set.configuration_policy.configurations_policy.values())
        cls.configuration_attribution_parameters.total_formation_size = int(sum(
            cls.configuration_attribution_parameters.formation_amounts))
        cls.configuration_attribution_parameters.platform_type = platform_property_set.platform_type
        cls.configuration_attribution_parameters.formation_amounts_intervals = [
            range(int(sum(cls.configuration_attribution_parameters.formation_amounts[0:i])),
                  int(sum(cls.configuration_attribution_parameters.formation_amounts[0:i + 1])))
            for i in range(0, len(cls.configuration_attribution_parameters.formation_amounts))]

    @classmethod
    def _calc_number_variables(cls) -> int:
        return int(sum(cls.configuration_attribution_parameters.formation_amounts) *
                   cls.configuration_attribution_parameters.configuration_options_size)

    @classmethod
    def _calc_configuration_options_constraints(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.configuration_attribution_parameters.configuration_options_size
        total_formation_size = cls.configuration_attribution_parameters.total_formation_size
        constraints_coefficients = np.zeros((total_formation_size, num_vars))
        for i in range(total_formation_size):
            constraints_coefficients[i, i * configuration_options_size: (i + 1) * configuration_options_size] = 1
        return constraints_coefficients.tolist()

    @classmethod
    def _calc_configuration_options_bounds(cls) -> Any:
        total_formation_size = cls.configuration_attribution_parameters.total_formation_size
        bounds = np.ones(total_formation_size)
        return bounds.tolist()

    @classmethod
    def _calc_configuration_policy_constraints(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.configuration_attribution_parameters.configuration_options_size
        formation_amounts = cls.configuration_attribution_parameters.formation_amounts
        formation_sizes = cls.configuration_attribution_parameters.formation_sizes
        constraints_coefficients = np.zeros((configuration_options_size, num_vars))
        for i in range(configuration_options_size):
            for j in range(len(formation_amounts) - 1):
                constraints_coefficients[i, i: int(formation_amounts[j] *
                                                   configuration_options_size):configuration_options_size] =\
                    formation_sizes[j]
                constraints_coefficients[i, i + int(formation_amounts[j] *
                                                    configuration_options_size)::configuration_options_size] = \
                    formation_sizes[j + 1]
        return constraints_coefficients.tolist()

    @classmethod
    def _calc_configuration_policy_bounds(cls) -> [float]:
        weights = cls.configuration_attribution_parameters.configurations_policy
        fleet_size = cls.configuration_attribution_parameters.fleet_size
        bounds = [weight * fleet_size for weight in weights]
        return bounds

    @classmethod
    def _calc_objective_coefficients(cls) -> Any:
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.configuration_attribution_parameters.configuration_options_size
        formation_amounts = cls.configuration_attribution_parameters.formation_amounts
        formation_sizes = cls.configuration_attribution_parameters.formation_sizes
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
    def _get_formation_size_type(cls, index: int) -> FormationSize:
        formation_amounts_intervals = cls.configuration_attribution_parameters.formation_amounts_intervals
        for interval in formation_amounts_intervals:
            if index in interval:
                formation_size_idx = formation_amounts_intervals.index(interval)
                return cls.configuration_attribution_parameters.formation_sizes[formation_size_idx]

    @classmethod
    def _export_drone_formation_amounts(cls, variables) -> DroneFormationsPerTypeAmounts:
        formation_amounts = DroneFormations.create_default_drone_formations_amounts(
            cls.configuration_attribution_parameters.platform_type)
        num_vars = cls._calc_number_variables()
        configuration_options_size = cls.configuration_attribution_parameters.configuration_options_size
        platform_type = cls.configuration_attribution_parameters.platform_type
        variables = [variables[j].solution_value() for j in range(num_vars)]
        chosen_formations_indices = [i % configuration_options_size for i, x in enumerate(variables) if x == 1.0]
        for i in range(len(chosen_formations_indices)):
            formation_size = cls._get_formation_size_type(i)
            configuration = cls.configuration_attribution_parameters.configurations[chosen_formations_indices[i]]
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
