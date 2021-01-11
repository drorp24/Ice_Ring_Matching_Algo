import unittest

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import PackageConfiguration, DroneType
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationsPolicy, DroneSetProperties


class TestDroneSetProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dftp = DroneFormationTypePolicy({DroneFormationType.QUAD: 0.3, DroneFormationType.PAIR: 0.7})
        cls.pcp = PackageConfigurationsPolicy({PackageConfiguration.SMALL_X8: 0.3, PackageConfiguration.LARGE_X2: 0.2,
                                               PackageConfiguration.MEDIUM_X4: 0.5})
        cls.dsp = DroneSetProperties(DroneType.drone_type_1, cls.dftp, cls.pcp, 10)

    def test_drone_formation_to_json(self):
        self.dftp.to_json('common/entities/base_entities/fleet/tests/jsons/dftp_test_file.json')
        dftp_dict = JsonableBaseEntity.json_to_dict(
            'common/entities/base_entities/fleet/tests/jsons/dftp_test_file.json')
        drone_formation_type_policy = DroneFormationTypePolicy.dict_to_obj(dftp_dict)
        print(drone_formation_type_policy)

    def test_package_configuration_policy_to_json(self):
        self.pcp.to_json('common/entities/base_entities/fleet/tests/jsons/pcp_test_file.json')
        pcp_dict = JsonableBaseEntity.json_to_dict(
            'common/entities/base_entities/fleet/tests/jsons/pcp_test_file.json')
        package_configuration_policy = PackageConfigurationsPolicy.dict_to_obj(pcp_dict)
        print(package_configuration_policy)

    def test_drone_set_properties_to_json(self):
        self.dsp.to_json('common/entities/base_entities/fleet/tests/jsons/dsp_test_file.json')
        dsp_dict = JsonableBaseEntity.json_to_dict(
            'common/entities/base_entities/fleet/tests/jsons/dsp_test_file.json')
        drone_set_properties = DroneSetProperties.dict_to_obj(dsp_dict)
        print(drone_set_properties)
