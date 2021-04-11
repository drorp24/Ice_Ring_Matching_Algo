import unittest
from datetime import timedelta

from pathlib import Path

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.drone import PackageConfiguration, DroneType
from common.entities.base_entities.drone_formation import DroneFormationType
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.drone_loading_station import DroneLoadingStation
from common.entities.base_entities.entity_id import EntityID
from common.entities.base_entities.fleet.fleet_property_sets import DroneFormationTypePolicy, \
    PackageConfigurationPolicy, DroneSetProperties
from common.entities.base_entities.temporal import TimeWindowExtension, TimeDeltaExtension
from common.entities.base_entities.tests.test_drone_delivery import ZERO_TIME
from geometry.geo_factory import create_point_2d


class TestDroneSetProperties(unittest.TestCase):

    base_path = 'common/entities/base_entities/fleet/tests/jsons/'
    dftp_json_path = Path('%sdftp_test_file.png' % base_path)
    pcp_json_path = Path('%spcp_test_file.png' % base_path)
    dsp_json_path = Path('%sdsp_test_file.png' % base_path)

    @classmethod
    def setUpClass(cls):
        cls.dftp = DroneFormationTypePolicy({DroneFormationType.QUAD: 0.3, DroneFormationType.PAIR: 0.7})
        cls.pcp = PackageConfigurationPolicy({PackageConfiguration.SMALL_X8: 0.3, PackageConfiguration.LARGE_X2: 0.2,
                                              PackageConfiguration.MEDIUM_X4: 0.5})
        cls.loading_dock = DroneLoadingDock(EntityID.generate_uuid(),
                         DroneLoadingStation(EntityID.generate_uuid(), create_point_2d(0, 0)),
                         DroneType.drone_type_1,
                         TimeWindowExtension(
                             since=ZERO_TIME,
                             until=ZERO_TIME.add_time_delta(
                                 TimeDeltaExtension(timedelta(hours=5)))))
        cls.dsp = DroneSetProperties(drone_type=DroneType.drone_type_1,
                                     drone_formation_policy=cls.dftp,
                                     package_configuration_policy=cls.pcp,
                                     start_loading_dock=cls.loading_dock,
                                     end_loading_dock=cls.loading_dock,
                                     drone_amount=10)

    @classmethod
    def tearDownClass(cls):
        cls.dftp_json_path.unlink()
        cls.pcp_json_path.unlink()
        cls.dsp_json_path.unlink()

    def test_drone_formation_to_json(self):
        self.dftp.to_json(self.dftp_json_path)
        dftp_dict = JsonableBaseEntity.json_to_dict(self.dftp_json_path)
        drone_formation_type_policy = DroneFormationTypePolicy.dict_to_obj(dftp_dict)
        self.assertEqual(drone_formation_type_policy, self.dftp)

    def test_package_configuration_policy_to_json(self):
        self.pcp.to_json(self.pcp_json_path)
        pcp_dict = JsonableBaseEntity.json_to_dict(self.pcp_json_path)
        package_configuration_policy = PackageConfigurationPolicy.dict_to_obj(pcp_dict)
        self.assertEqual(package_configuration_policy, self.pcp)

    def test_drone_set_properties_to_json(self):
        self.dsp.to_json(self.dsp_json_path)
        dsp_dict = JsonableBaseEntity.json_to_dict(self.dsp_json_path)
        drone_set_properties = DroneSetProperties.dict_to_obj(dsp_dict)
        self.assertEqual(drone_set_properties, self.dsp)
