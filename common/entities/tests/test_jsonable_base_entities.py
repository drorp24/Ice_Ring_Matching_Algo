import unittest
from random import Random

from common.entities.customer_delivery import CustomerDeliveryDistribution, CustomerDelivery
from common.entities.delivery_option import DeliveryOption, DeliveryOptionDistribution
from common.entities.delivery_request import DeliveryRequestDistribution, DeliveryRequest
from common.entities.package_delivery_plan import PackageDeliveryPlan, PackageDeliveryPlanDistribution

from common.entities.base_entity import JsonableBaseEntity


class BasicPackageTestCase(unittest.TestCase):

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
        self.pdp1.to_json('jsons/pdp_test_file.json')
        pdp_dict = JsonableBaseEntity.json_to_dict('jsons/pdp_test_file.json')
        self.assertEqual(self.pdp1, PackageDeliveryPlan.dict_to_obj(pdp_dict))

    def test_cd_to_dict(self):
        cd_dict1 = self.cd1.__dict__()
        cd2 = CustomerDelivery.dict_to_obj(cd_dict1)
        cd_dict2 = cd2.__dict__()
        self.assertEqual(self.cd1, cd2)
        self.assertEqual(cd_dict1, cd_dict2)

    def test_cd_to_json(self):
        self.cd1.to_json('jsons/cd_test_file.json')
        cd_dict = JsonableBaseEntity.json_to_dict('jsons/cd_test_file.json')
        self.assertEqual(self.cd1, CustomerDelivery.dict_to_obj(cd_dict))

    def test_do_to_dict(self):
        do_dict1 = self.do1.__dict__()
        do2 = DeliveryOption.dict_to_obj(do_dict1)
        do_dict2 = do2.__dict__()
        self.assertEqual(self.do1, do2)
        self.assertEqual(do_dict1, do_dict2)

    def test_do_to_json(self):
        self.do1.to_json('jsons/do_test_file.json')
        do_dict = JsonableBaseEntity.json_to_dict('jsons/do_test_file.json')
        self.assertEqual(self.do1, DeliveryOption.dict_to_obj(do_dict))

    def test_dr_to_dict(self):
        dr_dict1 = self.dr1.__dict__()
        dr2 = DeliveryRequest.dict_to_obj(dr_dict1)
        dr_dict2 = dr2.__dict__()
        self.assertEqual(self.dr1, dr2)
        self.assertEqual(dr_dict1, dr_dict2)

    def test_dr_to_json(self):
        self.dr1.to_json('jsons/dr_test_file.json')
        dr_dict = JsonableBaseEntity.json_to_dict('jsons/dr_test_file.json')
        self.assertEqual(self.dr1, DeliveryRequest.dict_to_obj(dr_dict))