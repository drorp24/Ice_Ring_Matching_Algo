import math
from abc import ABCMeta
from random import Random
from typing import Dict, List, Union
from uuid import UUID

from common.entities.distribution.distribution import Distribution, Range, UniformDistribution, HierarchialDistribution
from geometry.geo2d import Point2D


def initialize_internal(MetaClassToDistrib: ABCMeta,
                        map_from_attrib_to_internal_distrib: Dict[str, object]) -> object:
    internal_dict = dict(
        map(lambda x: (x[0], x[1].__dict__()) if not (isinstance(x[1], UUID) or isinstance(x[1], str))
        else (x[0], str(x[1])), map_from_attrib_to_internal_distrib.items()))
    internal_dict['__class__'] = MetaClassToDistrib.__name__
    return MetaClassToDistrib.dict_to_obj(internal_dict)


def choose_rand_by_attrib(internal_sample_dict: Dict[str, Distribution], random: Random, amount: int = 1) -> Dict[
    str, list]:
    return dict(map(lambda x: (x[0], x[1].choose_rand(random=random, amount=amount)), internal_sample_dict.items()))


def convert_list_dict_to_individual_dicts(attrib_to_lists: Dict) -> List[Dict[str, object]]:
    keys = list(attrib_to_lists.keys())
    amount_of_vals_per_key = len(attrib_to_lists[keys[0]])
    return [{k: attrib_to_lists[k][i] for k in keys} for i in range(amount_of_vals_per_key)]


def extract_amount_in_range(amount_range: Union[int, Range], random: Random) -> int:
    if isinstance(amount_range, Range):
        amount_range = math.floor(UniformDistribution(value_range=amount_range).choose_uniform_in_range(random))
    return amount_range


def add_base_point_to_relative_points(relative_points: List[Point2D], base_point: Point2D):
    return [base_point.add_vector(p.to_vector()) for p in relative_points]


def get_updated_internal_amount(distribution: HierarchialDistribution,
                                amount: Dict[type, Union[int, Range]]) -> Dict[type, int]:
    try:
        internal_amount = get_base_amount(distribution)
        internal_amount.update(amount)
        if distribution.distribution_class() not in internal_amount.keys():
            raise UndefinedBaseAmountException()
        return internal_amount
    except TypeError:
        raise UndefinedBaseAmountException()


def get_base_amount(distribution: HierarchialDistribution) -> Dict[type, int]:
    return {d: 1 for d in distribution.get_all_internal_types()}


class UndefinedBaseAmountException(Exception):
    pass
