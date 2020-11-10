import unittest
from pprint import pprint

from common.entities.delivery_request import generate_dr_distribution, PriorityDistribution
from common.entities.delivery_request_generator import DeliveryRequestDatasetGenerator, DeliveryRequestDatasetStructure


class BasicDeliveryRequestGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drs = 50
        cls.num_of_do_per_dr = 15
        cls.num_of_cd_per_do = 8
        cls.num_of_pdp_per_cd = 3

        dr_distribution = generate_dr_distribution(priority_distribution=PriorityDistribution([1, 2, 3, 4, 5]))

        cls.ds = DeliveryRequestDatasetStructure(num_of_delivery_requests=cls.num_of_drs,
                                                 num_of_delivery_options_per_delivery_request=cls.num_of_do_per_dr,
                                                 num_of_customer_deliveries_per_delivery_option=cls.num_of_cd_per_do,
                                                 num_of_package_delivery_plan_per_customer_delivery=cls.num_of_pdp_per_cd,
                                                 delivery_request_distribution=dr_distribution)
        cls.dr_dataset = DeliveryRequestDatasetGenerator.generate(cls.ds)

    def test_num_of_drs(self):
        self.assertEqual(len(self.dr_dataset), self.num_of_drs)

    def test_num_of_do_per_dr(self):
        self.assertEqual(len(self.dr_dataset[0].delivery_options), self.num_of_do_per_dr)

    def test_num_of_cd_per_do(self):
        self.assertEqual(len(self.dr_dataset[0].delivery_options[0].customer_deliveries), self.num_of_cd_per_do)

    def test_num_of_cd_per_do(self):
        self.assertEqual(len(self.dr_dataset[0].delivery_options[0].customer_deliveries[0].package_delivery_plans),
                         self.num_of_pdp_per_cd)

    def test_to_dict(self):
        pprint(self.dr_dataset[0].__dict__())
