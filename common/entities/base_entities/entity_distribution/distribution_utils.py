# import re
# from abc import ABCMeta
# from random import Random
# from typing import Dict, List
# from uuid import UUID
#
# from common.entities.distribution.distribution import Distribution
# from geometry.geo2d import Point2D
#
#
# class LocalDistribution:
#
#     def __init__(self, MetaClass: ABCMeta,
#                  attrib_distributions: Dict[str, Distribution]):
#         self._MetaClass = MetaClass
#         self._attrib_distributions = attrib_distributions
#
#     def choose_rand(self, amounts: Dict[ABCMeta, int], random=Random()):
#         if issubclass(self._MetaClass, InternallySamplable):
#             return [[attrib[1].choose_rand(amounts=amounts, random=random) for _ in range(amounts[self._MetaClass])] for
#                     attrib in self._attrib_distributions.items()]
#         per_attribute_dicts = LocalDistribution.choose_rand_by_attrib(self._attrib_distributions, random,
#                                                                       amounts[self._MetaClass])
#         per_instance_dicts = LocalDistribution.convert_list_dict_to_individual_dicts(per_attribute_dicts)
#         return [LocalDistribution.initialize_internal(self._MetaClass, k) for k in per_instance_dicts]
#
#     @staticmethod
#     def initialize_internal(MetaClassToDistrib: ABCMeta,
#                             map_from_attrib_to_internal_distrib: Dict[str, object]) -> object:
#         internal_dict = dict(
#             map(lambda x: (x[0], x[1].__dict__()) if not (isinstance(x[1], UUID) or isinstance(x[1], str))
#             else (x[0], str(x[1])), map_from_attrib_to_internal_distrib.items()))
#         internal_dict['__class__'] = MetaClassToDistrib.__name__
#         return MetaClassToDistrib.dict_to_obj(internal_dict)
#
#     @staticmethod
#     def choose_rand_by_attrib(internal_sample_dict: Dict[str, Distribution], random: Random, amount: int = 1) -> Dict[
#         str, list]:
#         return dict(map(lambda x: (x[0], x[1].choose_rand(random=random, amount=amount)), internal_sample_dict.items()))
#
#     @staticmethod
#     def convert_list_dict_to_individual_dicts(attrib_to_lists: Dict) -> List[Dict[str, object]]:
#         keys = list(attrib_to_lists.keys())
#         amount_of_vals_per_key = len(attrib_to_lists[keys[0]])
#         return [{k: attrib_to_lists[k][i] for k in keys} for i in range(amount_of_vals_per_key)]
#
#     @staticmethod
#     def add_base_point_to_locations(per_location_attribute_dicts: Dict[str, List[Point2D]], base_point: Point2D):
#         return {item[0]: [base_point.add_vector(p.to_vector()) for p in item[1]] for item in
#                 per_location_attribute_dicts.items()}
#
#     @staticmethod
#     def get_module_fingerprint_from_class(klass: ABCMeta):
#         word_separation_list = re.findall('[A-Z][^A-Z]*', klass.__name__)
#         class_name = sum([word + '_' for word in word_separation_list])[:-1]
#         entity_location = 'common.entities.' + class_name
#         entity_name = klass.__name__
#         return entity_location, entity_name
