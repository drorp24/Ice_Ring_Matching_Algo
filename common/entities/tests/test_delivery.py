import unittest
from input.delivery_requests_json_converter import create_delivery_requests_from_file


class BasicDeliveryGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dr = create_delivery_requests_from_file('DeliveryRequestTest.json')

    def test_customer_delivery_length(self):
        self.assertEqual(len(self.dr[0].delivery_options[0].customer_deliveries), 1)

    def test_delivery_option_length(self):
        self.assertEqual(len(self.dr[0].delivery_options), 2)

    def test_delivery_request_length(self):
        self.assertEqual(len(self.dr), 2)

    def test_delivery_request_time_window(self):
        self.assertFalse(self.dr[0].time_window.since > self.dr[0].time_window.until)

    def test_delivery_request_priority(self):
        self.assertEqual(self.dr[0].priority, 10)
