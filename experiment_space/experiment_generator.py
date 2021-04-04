import dataclasses
import itertools
from random import Random
from typing import List, Union


class Options:
    """
        Given any class, if you need to generate multiple variants of the class, with local changes to it, you can use
        the 'create_options_class' functionality. This is useful in the context of exhaustive and probabilistic
        experimentation or analysis of how specific parameters, of the data or solvers, effect algo results.

        Simple Example:
            Given class Foo, with attributes a, b, c and given the instance foo = Foo(5, 'ok', 4.2)
            foo_options = create_options_class(foo()) will generate FooOptions([5], ['ok'], [4.2])

            you can then append or overwrite the values in FooOptions:
            foo_options.a = [3,2] and foo_options
            foo_options.b.append('not ok')

            The you can generate the cartesian product of all options or randomly sample from them:

            foo_options.calc_cartesian_product() ->
                [Foo(3, 'ok', 4.2), Foo(3, 'not_ok', 4.2), Foo(2, 'ok', 4.2), Foo(2, 'not_ok', 4.2)]

            foo_options.calc_random_k(amount=2) ->
                [Foo(2, 'ok', 4.2), Foo(3, 'not_ok', 4.2)]
    """

    def get_first_sample(self):
        d = {k: v[0] for k, v in self.__dict__.items() if k is not 'internal_class' and k[:1] != '_'}
        a = self.__getattr__(self, 'internal_class')
        return a(**d)

    def calc_cartesian_product(self):
        options = Options.to_dict(self)
        options = {
            k: [{'internal_list': Options.calc_cartesian_product(i)} if Options.is_options_class(i) else i for i in v]
            for k, v in options.items()}
        options = Options._extract_internal_list(options)
        items = Options._dict_of_lists_to_generator_of_dicts(options)
        klass = self.__dict__.get('internal_class')
        d_list = list(items)
        return [klass(**d) for d in d_list]

    def calc_random_k(self, amount: int = 1, random: Random = Random(42)):
        options = Options.to_dict(self)
        options = {
            k: [{'internal_list': Options.calc_random_k(i, amount)} if Options.is_options_class(i) else i for i in v]
            for k, v in options.items()}
        options = Options._extract_internal_list(options)
        items = Options._dict_of_lists_to_generator_of_dicts(options)
        klass = self.__dict__.get('internal_class')
        d_list = random.choices(list(items), k=amount)
        return [klass(**d) for d in d_list]

    def to_dict(self):
        return {i[0]: i[1] for i in self.__dict__.items() if
                i[:1] != '_' and i[0] is not 'internal_class' and isinstance(i[1], list)}

    @staticmethod
    def _extract_internal_list(options):
        return {op[0]: op[1][0]['internal_list'] if isinstance(op[1], list) and isinstance(op[1][0], dict)
                                                    and 'internal_list' in op[1][0].keys() else op[1] for
                op in options.items()}

    @staticmethod
    def _dict_of_lists_to_generator_of_dicts(options):
        return (dict(zip(options.keys(), x)) for x in itertools.product(*options.values()))

    @staticmethod
    def is_options_class(i):
        return hasattr(i, '__name__') and 'Options' in i.__name__


def _flatten(input_list: Union[List, object]) -> Union[List, object]:
    return [item for sublist in input_list for item in sublist] if isinstance(input_list, list) else input_list


def _extract_properties_from_class(base_instance):
    return [k for k in type(base_instance).__dict__.items() if
            k[:1] != '_' and not callable(getattr(type(base_instance), k))]


def _extract_properties_option_from_class(base_instance, hierarchical_classes: List[str]):
    if dataclasses.is_dataclass(base_instance):
        d = {member: [_calc_internal_extract(base_instance.__getattribute__(member), hierarchical_classes)] for member
             in base_instance.__annotations__.keys()}
    else:
        d = {k: [_calc_internal_extract(base_instance.__getattribute__(k), hierarchical_classes)] for k, v in
             type(base_instance).__dict__.items() if k[:1] != '_' and not callable(getattr(type(base_instance), k))}
    return d


def _calc_internal_extract(base_instance, hierarchical_classes: List[str]):
    if type(base_instance).__name__ in hierarchical_classes:
        internal_extracted = create_options_class(base_instance, hierarchical_classes)
        return internal_extracted
    return base_instance


def create_options_class(base_instance: object, hierarchical_classes: List[str] = []) -> Options:
    internal_extracted = {'internal_class': type(base_instance)}
    internal_extracted.update(_extract_properties_option_from_class(base_instance, hierarchical_classes))
    return type(type(base_instance).__name__ + 'Options', (Options,), internal_extracted)
