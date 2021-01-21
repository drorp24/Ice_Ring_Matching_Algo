from pathlib import Path
from unittest import TestCase

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.zone import Zone
from geometry.geo_factory import create_polygon_2d, create_point_2d


class ZoneTestCase(TestCase):
    zone_json_path_str = 'common/entities/base_entities/tests/jsons/zone_test_file.json'

    @classmethod
    def setUpClass(cls):
        pass
        cls.polygon_2d = create_polygon_2d(
            [create_point_2d(100, 50), create_point_2d(100, 150), create_point_2d(200, 150),
             create_point_2d(200, 50)])
        cls.zone_obj = Zone(shape=cls.polygon_2d)

    @classmethod
    def tearDownClass(cls):
        Path(cls.zone_json_path_str).unlink()

    def test_zone_to_dict(self):
        zone_dict = self.zone_obj.__dict__()
        expected_zone_obj = Zone.dict_to_obj(zone_dict)
        expected_zone_dict = expected_zone_obj.__dict__()
        self.assertEqual(zone_dict, expected_zone_dict)
        self.assertEqual(self.zone_obj, expected_zone_obj)

    def test_match_config_from_json(self):
        self.zone_obj.to_json(self.zone_json_path_str)
        expected_zone_dict = JsonableBaseEntity.json_to_dict(self.zone_json_path_str)
        expected_zone_obj = Zone.dict_to_obj(expected_zone_dict)

        self.assertEqual(self.zone_obj, expected_zone_obj)
