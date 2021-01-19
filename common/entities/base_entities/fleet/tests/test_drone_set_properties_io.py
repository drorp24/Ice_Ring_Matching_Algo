import unittest

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import PackageConfiguration, DroneType
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationPolicy, DroneSetProperties


class TestDroneSetProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dftp = DroneFormationTypePolicy({DroneFormationType.QUAD: 0.3, DroneFormationType.PAIR: 0.7})
        cls.pcp = PackageConfigurationPolicy({PackageConfiguration.SMALL_X8: 0.3, PackageConfiguration.LARGE_X2: 0.2,
                                              PackageConfiguration.MEDIUM_X4: 0.5})
        cls.dsp = DroneSetProperties(DroneType.drone_type_1, cls.dftp, cls.pcp, 10)

    def test_drone_formation_to_json(self):
        file_path = 'common/entities/base_entities/fleet/tests/jsons/dftp_test_file.json'
        self.dftp.to_json(file_path)
        dftp_dict = JsonableBaseEntity.json_to_dict(file_path)
        drone_formation_type_policy = DroneFormationTypePolicy.dict_to_obj(dftp_dict)
        self.assertEqual(drone_formation_type_policy, self.dftp)

    def test_package_configuration_policy_to_json(self):
        file_path = 'common/entities/base_entities/fleet/tests/jsons/pcp_test_file.json'
        self.pcp.to_json(file_path)
        pcp_dict = JsonableBaseEntity.json_to_dict(file_path)
        package_configuration_policy = PackageConfigurationPolicy.dict_to_obj(pcp_dict)
        self.assertEqual(package_configuration_policy, self.pcp)

    def test_drone_set_properties_to_json(self):
        file_path = 'common/entities/base_entities/fleet/tests/jsons/dsp_test_file.json'
        self.dsp.to_json(file_path)
        dsp_dict = JsonableBaseEntity.json_to_dict(file_path)
        drone_set_properties = DroneSetProperties.dict_to_obj(dsp_dict)
        self.assertEqual(drone_set_properties, self.dsp)
