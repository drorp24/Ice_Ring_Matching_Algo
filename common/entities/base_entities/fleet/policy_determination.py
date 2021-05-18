from dataclasses import dataclass
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
import numpy as np
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.drone import DroneTypeToPackageConfigurationOptions, PackageTypeAmountMap
from matching.matcher_config import MatcherConfig
from common.math.lp_solver import LPSolver, LPData, LPParameters
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.fleet.fleet_property_sets import PackageConfigurationPolicy


@dataclass
class PolicyConfigDeterminationParameters:
    quantities_per_loading_dock: []
    drones_per_dock: []
    reloads_per_dock : []
    required_quantities_per_type: []
    loading_docks : []


@dataclass
class PolicyPerDock:
    policies: {DroneLoadingDock, PackageConfigurationPolicy}
    unserved: float


class FleetPolicyDeterminationAttribution:
    policy_determination_config: PolicyConfigDeterminationParameters = \
        PolicyConfigDeterminationParameters ([], [], [], [], [])

    @classmethod
    def extract_parameters(cls, drone_set_properties_list: [DroneSetProperties],
                           config_obj: MatcherConfig, requirements_per_type):
        cls.policy_determination_config.quantities_per_loading_dock = cls._calc_quantities_matrix(drone_set_properties_list)
        cls.policy_determination_config.drones_per_dock = [drone_set_properties.drone_amount for drone_set_properties in drone_set_properties_list]
        cls.policy_determination_config.reloads_per_dock = [config_obj.reload_per_vehicle for i in range(len(drone_set_properties_list))]
        cls.required_quantities_per_type = cls._calc_required_quantities (requirements_per_type)
        cls.policy_determination_config.loading_docks = [drone_set_properties.start_loading_dock for drone_set_properties in drone_set_properties_list]

    @classmethod
    def _calc_required_quantities (cls, requirements_per_type: {PackageType, float}):
        required_quantities = [0 for i in range(len(PackageType))]
        for j, type in enumerate(PackageType):
            for key, value in requirements_per_type.items():
                if key == type:
                    required_quantities[j] = value
                    break

        return required_quantities

    @classmethod
    def _calc_quantities_matrix (cls, drone_set_properties_list: [DroneSetProperties]):
        quantities = np.zeros(( len(PackageType), len (drone_set_properties_list)))
        for i in range (len (drone_set_properties_list)):
            for j, typePackage in enumerate(PackageType):
                for item in DroneTypeToPackageConfigurationOptions.drone_configurations_map[drone_set_properties_list[i].drone_type]:
                    quantity = PackageTypeAmountMap.get_package_type_amount(item.value, typePackage)
                    if quantity > 0:
                        quantities [j,i] = quantity
                        break

        return quantities

    @classmethod
    def _calc_number_variables(cls) -> int:
        return (len(cls.policy_determination_config.drones_per_dock) + 1) * len (PackageType)

    @classmethod
    def _calc_equality_constraints(cls):
        constraints_coefficients = np.zeros((len (PackageType), cls._calc_number_variables()))
        for i in range (len (PackageType)):
            s_index = i * len (cls.policy_determination_config.drones_per_dock)
            e_index = (i + 1) * (len (cls.policy_determination_config.drones_per_dock))
            for j in range (s_index ,  e_index):
                constraints_coefficients[i, j] = cls.policy_determination_config.quantities_per_loading_dock[i, j - s_index]\
                                                 * (1 + cls.policy_determination_config.reloads_per_dock[j - s_index])*\
                                                 (cls.policy_determination_config.drones_per_dock [j - s_index])
            constraints_coefficients [i, len (PackageType) * (len(cls.policy_determination_config.drones_per_dock)) + i] = 1

        return constraints_coefficients

    @classmethod
    def _calc_inequality_constraints(cls):
        constraints_coefficients = np.zeros((len (cls.policy_determination_config.drones_per_dock), cls._calc_number_variables()))
        for i in range(len (cls.policy_determination_config.drones_per_dock)):
            for j in range (len (PackageType)):
                constraints_coefficients[i, i + j * len (cls.policy_determination_config.drones_per_dock)] = 1

        return constraints_coefficients

    @classmethod
    def _calc_equality_bounds(cls):
        return cls.required_quantities_per_type

    @classmethod
    def _calc_inequality_bounds(cls):
        return [1 for i in range (len (cls.policy_determination_config.drones_per_dock))]

    @classmethod
    def _calc_objective_coefficients(cls):
        objective_coeff = [0 for i in range (cls._calc_number_variables())]
        for i in range (len (PackageType) * (len(cls.policy_determination_config.drones_per_dock)) , cls._calc_number_variables()):
            objective_coeff[i] = 1
        return objective_coeff

    @classmethod
    def _formulate_as_lp_problem(cls) -> LPData:
        data = {LPParameters.num_variables: cls._calc_number_variables(),
                LPParameters.inequality_constraints_coefficients: cls._calc_inequality_constraints (),
                LPParameters.inequality_bounds: cls._calc_inequality_bounds(),
                LPParameters.equality_constraints_coefficients:
                cls._calc_equality_constraints (),
                LPParameters.equality_bounds:
                    cls._calc_equality_bounds(),
                LPParameters.objective_coefficients: cls._calc_objective_coefficients()}
        return LPData(data)

    @classmethod
    def _export_policies_per_dock (cls, variables):
        solution = [variables[j].solution_value() for j in range(cls._calc_number_variables())]
        solution_dict = dict()
        for i in range (len (cls.policy_determination_config.loading_docks)):
            solution_dict [cls.policy_determination_config.loading_docks[i]] = dict()

            for j, typePackage in enumerate(PackageType):
                if solution [i + j * len (cls.policy_determination_config.drones_per_dock)] > 10 ** -4:
                    for item in DroneTypeToPackageConfigurationOptions.drone_configurations_map[cls.policy_determination_config.loading_docks[i].drone_type]:
                        quantity = PackageTypeAmountMap.get_package_type_amount(item.value, typePackage)
                        if quantity > 0:
                            solution_dict[cls.policy_determination_config.loading_docks[i]][item] =\
                                float(format (solution [i + j * len (cls.policy_determination_config.drones_per_dock)], ".4f"))

        solution_object = dict()
        for key, value in solution_dict.items() :
            solution_object[key] = PackageConfigurationPolicy(value)

        Unserved = sum (solution [len (PackageType) * (len(cls.policy_determination_config.drones_per_dock)) : ])
        return PolicyPerDock(solution_object, Unserved)

    @classmethod
    def solve(cls) -> PolicyPerDock :
        lp_data = cls._formulate_as_lp_problem()
        variables = LPSolver.set_variables(parameters=lp_data)
        lp_solver = LPSolver()
        lp_solver.set_equalities_constraints(parameters=lp_data, variables=variables)
        lp_solver.set_inequalities_constraints(parameters=lp_data, variables=variables)
        lp_solver.set_objective_coeffs(parameters=lp_data, variables=variables)
        lp_solver.set_minimization()
        lp_solver.solve()
        return cls._export_policies_per_dock (variables)
