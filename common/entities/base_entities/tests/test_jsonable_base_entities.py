import unittest
from random import Random

from common.entities.base_entities.base_entity import JsonableBaseEntity
from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.delivery_request import DeliveryRequest
from common.entities.base_entities.entity_distribution.customer_delivery_distribution import \
    CustomerDeliveryDistribution
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution
from common.entities.base_entities.entity_distribution.delivery_request_distribution import DeliveryRequestDistribution
from common.entities.base_entities.entity_distribution.package_delivery_plan_distribution import \
    PackageDeliveryPlanDistribution
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan


class BasicJsonableBaseEntitiesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdp1 = PackageDeliveryPlanDistribution().choose_rand(Random(10))[0]
        cls.cd1 = CustomerDeliveryDistribution().choose_rand(Random(42))[0]
        cls.do1 = DeliveryOptionDistribution().choose_rand(Random(42))[0]
        cls.dr1 = DeliveryRequestDistribution().choose_rand(Random(42))[0]

    def test_pdp_to_dict(self):
        pdp_dict1 = self.pdp1.__dict__()
        pdp2 = PackageDeliveryPlan.dict_to_obj(pdp_dict1)
        pdp_dict2 = pdp2.__dict__()
        self.assertEqual(self.pdp1, pdp2)
        self.assertEqual(pdp_dict1, pdp_dict2)

    def test_pdp_to_json(self):
        pdp_json_path = 'common/entities/base_entities/tests/jsons/pdp_test_file.json'
        self.pdp1.to_json(pdp_json_path)
        pdp_dict = JsonableBaseEntity.json_to_dict(pdp_json_path)
        self.assertEqual(self.pdp1, PackageDeliveryPlan.dict_to_obj(pdp_dict))

    def test_cd_to_dict(self):
        cd_dict1 = self.cd1.__dict__()
        cd2 = CustomerDelivery.dict_to_obj(cd_dict1)
        cd_dict2 = cd2.__dict__()
        self.assertEqual(self.cd1, cd2)
        self.assertEqual(cd_dict1, cd_dict2)

    def test_cd_to_json(self):
        cd_json_path = 'common/entities/base_entities/tests/jsons/cd_test_file.json'
        self.cd1.to_json(cd_json_path)
        cd_dict = JsonableBaseEntity.json_to_dict(cd_json_path)
        self.assertEqual(self.cd1, CustomerDelivery.dict_to_obj(cd_dict))

    def test_do_to_dict(self):
        do_dict1 = self.do1.__dict__()
        do2 = DeliveryOption.dict_to_obj(do_dict1)
        do_dict2 = do2.__dict__()
        self.assertEqual(self.do1, do2)
        self.assertEqual(do_dict1, do_dict2)

    def test_do_to_json(self):
        do_json_path = 'common/entities/base_entities/tests/jsons/do_test_file.json'
        self.do1.to_json(do_json_path)
        do_dict = JsonableBaseEntity.json_to_dict(do_json_path)
        self.assertEqual(self.do1, DeliveryOption.dict_to_obj(do_dict))

    def test_dr_to_dict(self):
        dr_dict1 = self.dr1.__dict__()
        dr2 = DeliveryRequest.dict_to_obj(dr_dict1)
        dr_dict2 = dr2.__dict__()
        self.assertEqual(self.dr1, dr2)
        self.assertEqual(dr_dict1, dr_dict2)

    def test_dr_to_json(self):
        dr_json_path = 'common/entities/base_entities/tests/jsons/dr_test_file.json'
        self.dr1.to_json(dr_json_path)
        dr_dict = JsonableBaseEntity.json_to_dict(dr_json_path)
        self.assertEqual(self.dr1, DeliveryRequest.dict_to_obj(dr_dict))
