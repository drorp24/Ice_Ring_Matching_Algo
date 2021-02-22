import unittest
from pathlib import Path
from random import Random
from typing import List

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_zone_delivery_request_distribution
from common.entities.base_entities.zone import Zone
from end_to_end.distribution.supplier_category_distribution import SupplierCategoryDistribution
from end_to_end.supplier_category import SupplierCategory
from geometry.distribution.geo_distribution import NormalPointsInMultiPolygonDistribution
from geometry.geo_factory import create_polygon_2d, create_point_2d, create_multipolygon_2d
from common.entities.base_entities.entity_id import EntityID
from uuid import uuid4


class BasicSupplierCategoryTests(unittest.TestCase):
    test_json_file_name = Path('end_to_end/tests/jsons/test_writing_supplier_category.json')
    test_with_zones_json_file_name = Path('end_to_end/tests/jsons/test_writing_supplier_category_with_zones.json')

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategoryDistribution().choose_rand(random=Random(),
                                                                           amount={DeliveryRequest: 10,
                                                                                   DroneLoadingDock: 1})
        zones = _create_zones(2)
        zone_delivery_request_distribution = build_zone_delivery_request_distribution(
            zones=zones,
            relative_dr_location_distribution=NormalPointsInMultiPolygonDistribution(
                multi_polygon=create_multipolygon_2d([zone.region for zone in zones]),
                max_centroids_per_polygon=2,
                sigma_x=0.01, sigma_y=0.01))

        cls.supplier_category_with_zones = SupplierCategoryDistribution(
            delivery_requests_distribution=zone_delivery_request_distribution).choose_rand(random=Random(),
                                                                                           amount={DeliveryRequest: 10,
                                                                                                   DroneLoadingDock: 1})

    @classmethod
    def tearDownClass(cls):
        cls.test_json_file_name.unlink()
        cls.test_with_zones_json_file_name.unlink()

    def test_supplier_category_amounts(self):
        self.assertEqual(len(self.supplier_category.delivery_requests), 10)
        self.assertEqual(len(self.supplier_category.drone_loading_docks), 1)

    def test_writing_supplier_category(self):
        self.supplier_category.to_json(self.test_json_file_name)
        loaded_supplier_category_dict = SupplierCategory.json_to_dict(self.test_json_file_name)
        loaded_supplier_category = self.supplier_category.dict_to_obj(loaded_supplier_category_dict)
        self.assertEqual(self.supplier_category, loaded_supplier_category)

    def test_writing_supplier_category_with_zones(self):
        self.supplier_category_with_zones.to_json(self.test_with_zones_json_file_name)
        loaded_supplier_category_dict = SupplierCategory.json_to_dict(self.test_with_zones_json_file_name)
        loaded_supplier_category = self.supplier_category_with_zones.dict_to_obj(loaded_supplier_category_dict)
        self.assertEqual(self.supplier_category_with_zones, loaded_supplier_category)

def _create_zones(zone_amount: int = 1) -> List[Zone]:
    return [
               Zone(create_polygon_2d([create_point_2d(35.03, 31.82),
                                       create_point_2d(35.03, 32.01),
                                       create_point_2d(35.3, 32.01),
                                       create_point_2d(35.3, 31.82)]),id = EntityID(uuid=uuid4())),
               Zone(create_polygon_2d([create_point_2d(35.03, 32.01),
                                       create_point_2d(35.09, 32.18),
                                       create_point_2d(35.3, 32.18),
                                       create_point_2d(35.3, 32.01)]),id = EntityID(uuid=uuid4()))
           ][0:zone_amount]