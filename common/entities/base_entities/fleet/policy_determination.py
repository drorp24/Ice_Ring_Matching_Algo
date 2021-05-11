from dataclasses import dataclass
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
import numpy as np
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.drone import DroneTypeToPackageConfigurationOptions, PackageTypeAmountMap
from matching.matcher_config import ConstraintsConfig, MatcherConfig
from common.math.mip_solver import MIPSolver, MIPData, MIPParameters
import copy
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.fleet.fleet_property_sets import PackageConfigurationPolicy

@dataclass
class PolicyConfigDeterminationParameters:
    quantities_per_loading_dock: []
    drones_per_fleet: []
    reloads_per_dock : []
    required_quantities_per_type: []
    loading_docks : []

@dataclass
class PolicyPerDock:
    Policies: {DroneLoadingDock, PackageConfigurationPolicy}

class fleetPolicyDeterminationAttribution:
    policy_determination_config: PolicyConfigDeterminationParameters = \
        PolicyConfigDeterminationParameters ([], [], [], [], [])

    @classmethod
    def extract_parameters(cls, drone_set_properties_list: [DroneSetProperties],
                           config_obj: MatcherConfig, requirements_per_type):
        cls.policy_determination_config.quantities_per_loading_dock = cls._calc_quantites_matrix(drone_set_properties_list)
        cls.policy_determination_config.drones_per_fleet = [drone_set_properties.drone_amount for drone_set_properties in drone_set_properties_list]
        cls.policy_determination_config.reloads_per_dock = [config_obj.reload_per_vehicle for i in range(len(drone_set_properties_list))]
        cls.required_quantities_per_type = copy.deepcopy (requirements_per_type)
        cls.policy_determination_config.loading_docks = [drone_set_properties.start_loading_dock for drone_set_properties in drone_set_properties_list]

        print (cls.policy_determination_config.quantities_per_loading_dock)
        print (cls.policy_determination_config.drones_per_fleet)
        print (cls.policy_determination_config.reloads_per_dock)
        print (cls.required_quantities_per_type)

    @classmethod
    def _calc_quantites_matrix (cls, drone_set_properties_list: [DroneSetProperties]):
        quantities = np.zeros(( len(PackageType), len (drone_set_properties_list)))
        for i in range (len (drone_set_properties_list)):
            j = 0
            for typePackage in PackageType:
                for item in DroneTypeToPackageConfigurationOptions.drone_configurations_map[drone_set_properties_list[i].drone_type]:
                    quantity = PackageTypeAmountMap.get_package_type_amount(item.value, typePackage)
                    if quantity > 0:
                        quantities [j,i] = quantity
                        break
                j = j + 1

        return quantities

    @classmethod
    def _calc_number_variables(cls) -> int:
        return ((len(cls.policy_determination_config.drones_per_fleet) + 1) * len (PackageType))

    #@staticmethod
    @classmethod
    def _calc_equality_constraints_1(cls):
        constraints_coefficients = np.zeros((len (PackageType), cls._calc_number_variables()))
        #print (constraints_coefficients)
        for i in range (len (PackageType)):
            s_index = i * len (cls.policy_determination_config.drones_per_fleet)
            e_index = (i + 1) * (len (cls.policy_determination_config.drones_per_fleet))
            #print(i)
            #print (s_index,  e_index)

            for j in range (s_index ,  e_index):
                #print(i, j)
                #print (cls.policy_determination_config.quantities_per_loading_dock[i, j - s_index])
                #print (1 + cls.policy_determination_config.reloads_per_dock[j - s_index])
                #print (cls.policy_determination_config.drones_per_fleet [j - s_index])
                #print (i,j)
                constraints_coefficients[i, j] = cls.policy_determination_config.quantities_per_loading_dock[i, j - s_index]\
                                                 * (1 + cls.policy_determination_config.reloads_per_dock[j - s_index])*\
                                                 (cls.policy_determination_config.drones_per_fleet [j - s_index])

            constraints_coefficients [i, len (PackageType) * (len(cls.policy_determination_config.drones_per_fleet)) + i] = 1

            print (constraints_coefficients)
        return constraints_coefficients

    @classmethod
    def _calc_equality_constraints_2(cls):
        constraints_coefficients = np.zeros((len (cls.policy_determination_config.drones_per_fleet), cls._calc_number_variables()))
        for i in range(len (cls.policy_determination_config.drones_per_fleet)):
            for j in range (len (PackageType)):
                constraints_coefficients[i, i + j * len (cls.policy_determination_config.drones_per_fleet)] = 1

        print (constraints_coefficients)
        return constraints_coefficients



    @classmethod
    def _calc_equality_bounds_1(cls):
        print (cls.required_quantities_per_type)
        return cls.required_quantities_per_type

    @classmethod
    def _calc_equality_bounds_2(cls):
        print ([1 for i in range (len (cls.policy_determination_config.drones_per_fleet))])
        return [1 for i in range (len (cls.policy_determination_config.drones_per_fleet))]

    @classmethod
    def _calc_objective_coefficients(cls):
        objective_coeff = [0 for i in range (cls._calc_number_variables())]
        for i in range (len (PackageType) * (len(cls.policy_determination_config.drones_per_fleet)) , cls._calc_number_variables()):
            objective_coeff[i] = 1
        print (objective_coeff)
        return objective_coeff

    @classmethod
    def _formulate_as_mip_problem(cls) -> MIPData:
        data = {MIPParameters.num_variables: cls._calc_number_variables(),
                MIPParameters.equality_constraints_coefficients:
                np.concatenate ((cls._calc_equality_constraints_1 (), cls._calc_equality_constraints_2 ()), axis=0),
                MIPParameters.equality_bounds:
                    cls._calc_equality_bounds_1() + cls._calc_equality_bounds_2(),
                MIPParameters.objective_coefficients: cls._calc_objective_coefficients()}
        return MIPData(data)

    @classmethod
    def _export_policies_per_dock (cls, variables):
        solution = [variables[j].solution_value() for j in range(cls._calc_number_variables())]
        solution_dict = dict()
        for i in range (len (cls.policy_determination_config.loading_docks)):
            solution_dict [cls.policy_determination_config.loading_docks[i]] = []
            j = 0
            for typePackage in PackageType:
                if solution [i + j * len (cls.policy_determination_config.drones_per_fleet)] > 0:
                    print (cls.policy_determination_config.loading_docks[i], typePackage, solution [i + j * len (cls.policy_determination_config.drones_per_fleet)])
                    for item in DroneTypeToPackageConfigurationOptions.drone_configurations_map[cls.policy_determination_config.loading_docks[i].drone_type]:
                        quantity = PackageTypeAmountMap.get_package_type_amount(item.value, typePackage)
                        if quantity > 0:
                            solution_dict[cls.policy_determination_config.loading_docks[i]].append ({item.name: solution [i + j * len (cls.policy_determination_config.drones_per_fleet)]})


                j = j + 1

        print (solution_dict)
        solution_object = dict()
        for key, value in solution_dict.items() :
            dict_policy = value [0]
            for i in range (1, len(value)):
                dict_policy.update (value [i])

            solution_object[key] = dict_policy



            #print (value)
            #print ([val for val in value])

            #for val in value:
            #    print({val_s[0]: val_s[1] for val_s in val.items()})


            #print (PackageConfigurationPolicy({val for val in value}))
        print (PolicyPerDock(solution_object))
        return PolicyPerDock(solution_object)





    @classmethod
    def solve(cls) :
        mip_data = cls._formulate_as_mip_problem()
        variables = MIPSolver.set_variables(parameters=mip_data)
        mip_solver = MIPSolver()
        mip_solver.set_equalities_constraints(parameters=mip_data, variables=variables)
        mip_solver.set_objective_coeffs(parameters=mip_data, variables=variables)
        mip_solver.set_minimization()
        mip_solver.solve()
        print (variables)
        print ([variables[j].solution_value() for j in range(cls._calc_number_variables())])
        cls._export_policies_per_dock (variables)

        #return cls._export_drone_formation_amounts(variables)



    #def _calc_constraints_coefficients(configuration_options_amount, formation_amounts, formation_sizes, num_vars):
    #    constraints_coefficients = np.zeros((configuration_options_amount, num_vars))
    #    for i in range(configuration_options_amount):
    #        for j in range(len(formation_amounts) - 1):
    #            index_jump = int(formation_amounts[j] * configuration_options_amount)
    #            constraints_coefficients[i, i: index_jump:configuration_options_amount] = formation_sizes[j]
    #            constraints_coefficients[i, i + index_jump::configuration_options_amount] = formation_sizes[j + 1]
    #    return constraints_coefficients.tolist()

    #@classmethod
    #def formulate_as_mip_problem(cls) -> MIPData:
    #    print (cls._calc_number_variables() )

    #    data = {MIPParameters.num_variables: cls._calc_number_variables(),
    #            MIPParameters.inequality_constraints_coefficients:
    #                cls._calc_configuration_policy_constraints() + cls._calc_configuration_options_constraints(),
    #            MIPParameters.inequality_bounds:
    #                cls._calc_configuration_policy_bounds() + cls._calc_configuration_options_bounds(),
    #            MIPParameters.objective_coefficients: cls._calc_objective_coefficients()}
    #    return MIPData(data)



