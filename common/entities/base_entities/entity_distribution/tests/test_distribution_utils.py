import unittest
from random import Random

from common.entities.base_entities.customer_delivery import CustomerDelivery
from common.entities.base_entities.delivery_option import DeliveryOption
from common.entities.base_entities.entity_distribution.delivery_option_distribution import DeliveryOptionDistribution
from common.entities.base_entities.entity_distribution.distribution_utils import extract_amount_in_range, \
    get_updated_internal_amount
from common.entities.base_entities.package_delivery_plan import PackageDeliveryPlan
from common.entities.distribution.distribution import Range


class BaseDistributionUtilsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.do_samples = DeliveryOptionDistribution()

    def test_extract_amount_in_range_input_range(self):
        amount_range = Range(5, 10)
        val = [extract_amount_in_range(amount_range, random=Random(i * 10)) in amount_range for i in range(100)]
        self.assertTrue(all(val))

    def test_extract_amount_in_range_input_int(self):
        amount_range = 8
        val = [extract_amount_in_range(amount_range, random=Random(i * 10)) == 8 for i in range(100)]
        self.assertTrue(all(val))

    def test_default_get_updated_internal_amount(self):
        amount = get_updated_internal_amount(distribution=DeliveryOptionDistribution, amount={})
        self.assertEqual(amount, {DeliveryOption: 1, CustomerDelivery: 1, PackageDeliveryPlan: 1})

    def test_get_updated_internal_amount(self):
        amount = get_updated_internal_amount(distribution=DeliveryOptionDistribution,
                                             amount={CustomerDelivery: Range(3, 6)})
        self.assertEqual(amount, {DeliveryOption: 1, CustomerDelivery: Range(3, 6), PackageDeliveryPlan: 1})
