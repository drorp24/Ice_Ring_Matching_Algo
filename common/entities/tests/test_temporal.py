import unittest
from datetime import date, time

from common.entities.temporal import DateTimeExtension, TimeWindowExtension


class BasicDateTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dt1 = DateTimeExtension(dt_date=date(2010, 10, 1), dt_time=time(6, 10, 5))
        cls.dt2 = DateTimeExtension(dt_date=date(2010, 10, 1), dt_time=time(7, 12, 5))
        cls.tw1 = TimeWindowExtension(cls.dt1, cls.dt2)

    def test_to_dict(self):
        dt1_dict = self.dt1.to_dict()
        expected_dict = {'date': {'year': 2010, 'month': 10, 'day': 1}, 'time': {'hour': 6, 'minute': 10, 'second': 5}}
        self.assertEqual(dt1_dict, expected_dict)

    def test_to_and_from_dict_equivalence(self):
        dt1_dict = self.dt1.to_dict()
        dt1_after_transformation = DateTimeExtension.from_dict(dt1_dict)
        self.assertEqual(self.dt1, dt1_after_transformation)

    def test_from_and_to_dict_equivalence(self):
        dt1_dict_after_to = self.dt1.to_dict()
        dt1_after_from = DateTimeExtension.from_dict(dt1_dict_after_to)
        dt1_dict_after_to_after_from = dt1_after_from.to_dict()
        self.assertEqual(dt1_dict_after_to, dt1_dict_after_to_after_from)

    def test_time_window_to_dict(self):
        tw1_dict = self.tw1.to_dict()
        expected_dict = {
            'since': {'date': {'year': 2010, 'month': 10, 'day': 1}, 'time': {'hour': 6, 'minute': 10, 'second': 5}},
            'until': {'date': {'year': 2010, 'month': 10, 'day': 1}, 'time': {'hour': 7, 'minute': 12, 'second': 5}}}
        self.assertEqual(tw1_dict, expected_dict)

    def test_time_window_from_dict(self):
        tw1_hard_coded_dict = {
            'since': {'date': {'year': 2010, 'month': 10, 'day': 1}, 'time': {'hour': 6, 'minute': 10, 'second': 5}},
            'until': {'date': {'year': 2010, 'month': 10, 'day': 1}, 'time': {'hour': 7, 'minute': 12, 'second': 5}}}
        tw_obj_after_from = TimeWindowExtension.from_dict(tw1_hard_coded_dict)
        self.assertEqual(self.tw1, tw_obj_after_from)
