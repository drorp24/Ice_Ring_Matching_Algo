import re
from abc import ABCMeta
from random import Random
from typing import Dict, List
from uuid import UUID

from common.entities.distribution.distribution import Distribution
from geometry.geo2d import Point2D


class LocalDistribution:

    @staticmethod
    def initialize_internal(MetaClassToDistrib: ABCMeta,
                            map_from_attrib_to_internal_distrib: Dict[str, object]) -> object:
        internal_dict = dict(
            map(lambda x: (x[0], x[1].__dict__()) if not (isinstance(x[1], UUID) or isinstance(x[1], str))
            else (x[0], str(x[1])), map_from_attrib_to_internal_distrib.items()))
        internal_dict['__class__'] = MetaClassToDistrib.__name__
        return MetaClassToDistrib.dict_to_obj(internal_dict)

    @staticmethod
    def choose_rand_by_attrib(internal_sample_dict: Dict[str, Distribution], random: Random, amount: int = 1) -> Dict[
        str, list]:
        return dict(map(lambda x: (x[0], x[1].choose_rand(random=random, amount=amount)), internal_sample_dict.items()))

    @staticmethod
    def convert_list_dict_to_individual_dicts(attrib_to_lists: Dict) -> List[Dict[str, object]]:
        keys = list(attrib_to_lists.keys())
        amount_of_vals_per_key = len(attrib_to_lists[keys[0]])
        return [{k: attrib_to_lists[k][i] for k in keys} for i in range(amount_of_vals_per_key)]

    @staticmethod
    def add_base_point_to_relative_points(relative_points: List[Point2D], base_point: Point2D):
        return [base_point.add_vector(p.to_vector()) for p in relative_points]

    @staticmethod
    def get_updated_internal_amount(distribution: type, amount: Dict[type, int]) -> Dict[type, int]:
        try:
            internal_amount = distribution.get_base_amount()
            internal_amount.update(amount)
            return internal_amount
        except:
            raise LocalDistribution.UndefinedBaseAmountException()

    class UndefinedBaseAmountException(Exception):
        pass
