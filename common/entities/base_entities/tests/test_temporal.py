import unittest
from datetime import date, time
from random import Random

from common.entities.base_entities.entity_distribution.temporal_distribution import ExactTimeWindowDistribution
from common.entities.base_entities.temporal import DateTimeExtension, TimeWindowExtension


class BasicTemporalTests(unittest.TestCase):

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


    def test_iso_to_dict_equivalence(self):
        iso_string ='2021-03-03T10:28:16.217305'
        excpected_dict={'__class__': 'DateTimeExtension','date': {'year': 2021, 'month': 3, 'day': 3}, 'time': {'hour': 10, 'minute': 28, 'second': 16}}
        time_after_conver = DateTimeExtension.extract_time_from_iso(iso_string)
        self.assertEqual(time_after_conver.__dict__(), excpected_dict)

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

    def test_exact_time_window_distribution(self):
        exact_tw_dist = ExactTimeWindowDistribution([self.tw1,
                                                     self.tw2,
                                                     self.tw3])
        actual_tw_1 = exact_tw_dist.choose_rand(Random(42), 1)
        actual_tw_2_3 = exact_tw_dist.choose_rand(Random(42), 2)
        self.assertEqual([self.tw1], actual_tw_1)
        self.assertEqual([self.tw2, self.tw3], actual_tw_2_3)
        self.assertRaises(RuntimeError, exact_tw_dist.choose_rand, (Random(42), 1))
