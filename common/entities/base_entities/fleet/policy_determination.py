from dataclasses import dataclass
from common.entities.base_entities.fleet.fleet_property_sets import DroneSetProperties
import numpy as np
from common.entities.base_entities.package import PackageType
from common.entities.base_entities.drone import DroneTypeToPackageConfigurationOptions, PackageTypeAmountMap
from matching.matcher_config import ConstraintsConfig, MatcherConfig


@dataclass
class PolicyConfigDeterminationParameters:
    quantities_per_loading_dock: []
    drones_per_fleet: []

class fleetPolicyDeterminationAttribution:
    policy_determination_config: PolicyConfigDeterminationParameters = \
        PolicyConfigDeterminationParameters ([], [])

    @classmethod
    def extract_parameters(cls, drone_set_properties_list: [DroneSetProperties],
                           config_obj: MatcherConfig):
        cls.policy_determination_config.quantities_per_loading_dock = cls._calc_quantites_matrix(drone_set_properties_list)
        cls.policy_determination_config.drones_per_fleet = [drone_set_properties.drone_amount for drone_set_properties in drone_set_properties_list]
        print (cls.policy_determination_config.quantities_per_loading_dock)
        print (cls.policy_determination_config.drones_per_fleet)

    #@classmethod
    #def prepare_parameters(cls, drone_set_properties_list: [DroneSetProperties]):
    #    cls.policy_determination_config.quantities_per_loading_dock = cls._calc_quantites_matrix(drone_set_properties_list)

    @classmethod
    def _calc_quantites_matrix (cls, drone_set_properties_list: [DroneSetProperties]):
        quantities = np.zeros((len (drone_set_properties_list), len(PackageType)))
        for i in range (len (drone_set_properties_list)):
            j = 0
            for typePackage in PackageType:
                for item in DroneTypeToPackageConfigurationOptions.drone_configurations_map[drone_set_properties_list[i].drone_type]:
                    quantity = PackageTypeAmountMap.get_package_type_amount(item.value, typePackage)
                    if quantity > 0:
                        quantities [i,j] = quantity
                j = j + 1

        return quantities



