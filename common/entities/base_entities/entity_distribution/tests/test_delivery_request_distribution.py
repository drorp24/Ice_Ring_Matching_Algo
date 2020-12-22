import unittest

from common.entities.base_entities.entity_distribution.delivery_request_distribution import PriorityDistribution
from common.entities.base_entities.entity_distribution.delivery_requestion_dataset_builder import \
    build_delivery_request_distribution
from common.entities.distribution.distribution import Range
from common.entities.generator.delivery_request_generator import DeliveryRequestDatasetGenerator, \
    DeliveryRequestDatasetStructure


class BasicDeliveryRequestDistributionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.num_of_drs = Range(5,10)
        cls.num_of_do_per_dr = Range(5,10)
        cls.num_of_cd_per_do = Range(5,10)
        cls.num_of_pdp_per_cd = Range(5,10)

        dr_distribution = build_delivery_request_distribution(
            priority_distribution=PriorityDistribution([1, 2, 3, 4, 5]))

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
