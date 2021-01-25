import unittest
from pathlib import Path
from random import Random

from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.drone_loading_dock import DroneLoadingDock
from end_to_end.distribution.supplier_category_distribution import SupplierCategoryDistribution
from end_to_end.supplier_category import SupplierCategory


class BasicSupplierCategoryTests(unittest.TestCase):

    test_json_file_name = Path('end_to_end/tests/jsons/test_writing_supplier_category.json')

    @classmethod
    def setUpClass(cls):
        cls.supplier_category = SupplierCategoryDistribution().choose_rand(random=Random(),
                                                          amount={DeliveryRequest: 10, DroneLoadingDock: 1})

    @classmethod
    def tearDownClass(cls):
        cls.test_json_file_name.unlink()

    def test_supplier_category_amounts(self):
        self.assertEqual(len(self.supplier_category.delivery_requests), 10)
        self.assertEqual(len(self.supplier_category.drone_loading_docks), 1)

    def test_writing_supplier_category(self):
        self.supplier_category.to_json(self.test_json_file_name)
        loaded_supplier_category_dict = SupplierCategory.json_to_dict(self.test_json_file_name)
        loaded_supplier_category = self.supplier_category.dict_to_obj(loaded_supplier_category_dict)
        self.assertEqual(self.supplier_category, loaded_supplier_category)
