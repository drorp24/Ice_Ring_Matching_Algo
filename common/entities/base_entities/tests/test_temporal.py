import unittest
from datetime import date, time

from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension


class BasicDateTime(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dt1 = DateTimeExtension(dt_date=date(2021, 10, 1), dt_time=time(6, 10, 5))
        cls.dt2 = DateTimeExtension(dt_date=date(2021, 10, 1), dt_time=time(7, 12, 5))
        cls.dt3 = DateTimeExtension(dt_date=date(2021, 10, 1), dt_time=time(8, 12, 5))
        cls.dt4 = DateTimeExtension(dt_date=date(2021, 10, 1), dt_time=time(9, 12, 5))
        cls.tw1 = TimeWindowExtension(cls.dt1, cls.dt2)
        cls.tw2 = TimeWindowExtension(cls.dt3, cls.dt4)
        cls.tw3 = TimeWindowExtension(cls.dt2, cls.dt3)
        cls.tw4 = TimeWindowExtension(cls.dt1, cls.dt4)

    def test_contains(self):
        self.assertTrue(self.dt1 in self.tw1)
        self.assertFalse(self.dt1 in self.tw3)
        self.assertTrue(self.tw2 in self.tw4)
        self.assertFalse(self.tw4 in self.tw2)
        self.assertTrue(self.tw1 in self.tw1)

    def test_to_dict(self):
        dt1_dict = self.dt1.__dict__()
        expected_dict = {'__class__': 'DateTimeExtension',
                         'date': {'day': 1, 'month': 10, 'year': 2021},
                         'time': {'hour': 6, 'minute': 10, 'second': 5}}
        self.assertEqual(dt1_dict, expected_dict)

    def test_to_and_from_dict_equivalence(self):
        dt1_dict = self.dt1.__dict__()
        dt1_after_transformation = DateTimeExtension.from_dict(dt1_dict)
        self.assertEqual(self.dt1, dt1_after_transformation)

    def test_from_and_to_dict_equivalence(self):
        dt1_dict_after_to = self.dt1.__dict__()
        dt1_after_from = DateTimeExtension.from_dict(dt1_dict_after_to)
        dt1_dict_after_to_after_from = dt1_after_from.__dict__()
        self.assertEqual(dt1_dict_after_to, dt1_dict_after_to_after_from)

    def test_time_window_to_dict(self):
        tw1_dict = self.tw1.__dict__()
        expected_dict = {'__class__': 'TimeWindowExtension',
                         'since': {'__class__': 'DateTimeExtension',
                                   'date': {'day': 1, 'month': 10, 'year': 2021},
                                   'time': {'hour': 6, 'minute': 10, 'second': 5}},
                         'until': {'__class__': 'DateTimeExtension',
                                   'date': {'day': 1, 'month': 10, 'year': 2021},
                                   'time': {'hour': 7, 'minute': 12, 'second': 5}}}
        self.assertDictEqual(tw1_dict, expected_dict)

    def test_time_window_from_dict(self):
        tw1_dict = {'__class__': 'TimeWindowExtension',
                    'since': {'__class__': 'DateTimeExtension', 'date': {'day': 1, 'month': 10, 'year': 2021},
                              'time': {'hour': 6, 'minute': 10, 'second': 5}},
                    'until': {'__class__': 'DateTimeExtension', 'date': {'day': 1, 'month': 10, 'year': 2021},
                              'time': {'hour': 7, 'minute': 12, 'second': 5}}}
        tw_obj_after_from = TimeWindowExtension.dict_to_obj(tw1_dict)
        self.assertEqual(self.tw1, tw_obj_after_from)

    def test_gt(self):
        self.assertTrue(self.dt1 < self.dt2)
        self.assertFalse(self.dt1 > self.dt2)
