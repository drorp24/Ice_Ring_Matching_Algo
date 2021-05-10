from dataclasses import dataclass
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
import numpy as np
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.drone import DroneTypeToPackageConfigurationOptions, PackageTypeAmountMap
from matching.matcher_config import ConstraintsConfig, MatcherConfig
from common.math.mip_solver import MIPSolver, MIPData, MIPParameters
import copy


@dataclass
class PolicyConfigDeterminationParameters:
    quantities_per_loading_dock: []
    drones_per_fleet: []
    reloads_per_dock : []
    required_quantities_per_type: []

class fleetPolicyDeterminationAttribution:
    policy_determination_config: PolicyConfigDeterminationParameters = \
        PolicyConfigDeterminationParameters ([], [], [], [])

    @classmethod
    def extract_parameters(cls, drone_set_properties_list: [DroneSetProperties],
                           config_obj: MatcherConfig, requirements_per_type):
        cls.policy_determination_config.quantities_per_loading_dock = cls._calc_quantites_matrix(drone_set_properties_list)
        cls.policy_determination_config.drones_per_fleet = [drone_set_properties.drone_amount for drone_set_properties in drone_set_properties_list]
        cls.policy_determination_config.reloads_per_dock = [config_obj.reload_per_vehicle for i in range(len(drone_set_properties_list))]
        cls.required_quantities_per_type = copy.deepcopy (requirements_per_type)

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
                j = j + 1

        return quantities

    @classmethod
    def _calc_number_variables(cls) -> int:
        return ((len(cls.policy_determination_config.drones_per_fleet) + 1) * len (PackageType))

    #@staticmethod
    @classmethod
    def calc_equality_constraints(cls):
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
    def calc_equality_bounds(cls):
        print (cls.required_quantities_per_type)
        return cls.required_quantities_per_type

    @classmethod
    def calc_objective_coefficients(cls):
        objective_coeff = [0 for i in range (cls._calc_number_variables())]
        for i in range (len (PackageType) * (len(cls.policy_determination_config.drones_per_fleet)) , cls._calc_number_variables()):
            objective_coeff[i] = 1
        print (objective_coeff)
        return objective_coeff








            #@staticmethod
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



