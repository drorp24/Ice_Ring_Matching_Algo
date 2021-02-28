import itertools
from random import Random
from typing import List, Union


class Options:

    def get_first_sample(self):
        d = {k: v[0] for k, v in self.__dict__.items() if k is not 'internal_class' and k[:1] != '_'}
        a = self.__getattribute__(self, 'internal_class')
        return a(**d)

    def calc_cartesian_product(self):
        options = Options.to_dict(self)
        options = {
            k: [{'internal_list': Options.calc_cartesian_product(i)} if Options.is_options_class(i) else i for i in v]
            for k, v in options.items()}
        options = Options.extract_internal_list(options)
        items = Options.dict_of_lists_to_generator_of_dicts(options)
        klass = self.__dict__.get('internal_class')
        d_list = list(items)
        return [klass(**d) for d in d_list]

    def calc_random_k(self, amount: int = 1, random: Random = Random(42)):
        options = Options.to_dict(self)
        options = {
            k: [{'internal_list': Options.calc_random_k(i, amount)} if Options.is_options_class(i) else i for i in v]
            for k, v in options.items()}
        options = Options.extract_internal_list(options)
        items = Options.dict_of_lists_to_generator_of_dicts(options)
        klass = self.__dict__.get('internal_class')
        d_list = random.choices(list(items), k=amount)
        return [klass(**d) for d in d_list]

    def to_dict(self):
        return {i[0]: i[1] for i in self.__dict__.items() if
                i[:1] != '_' and i[0] is not 'internal_class' and isinstance(i[1], list)}

    @staticmethod
    def extract_internal_list(options):
        return {op[0]: op[1][0]['internal_list']
        if isinstance(op[1], list) and isinstance(op[1][0], dict) and 'internal_list' in
           op[1][0].keys() else op[1] for op in options.items()}

    @staticmethod
    def dict_of_lists_to_generator_of_dicts(options):
        return (dict(zip(options.keys(), x)) for x in itertools.product(*options.values()))

    @staticmethod
    def is_options_class(i):
        return hasattr(i, '__name__') and 'Options' in i.__name__


def flatten(input: Union[List, object]) -> Union[List, object]:
    return [item for sublist in input for item in sublist] if isinstance(input, list) else input


def extract_properties_from_class(base_instance):
    return [k for k in type(base_instance).__dict__.items() if
            k[:1] != '_' and not callable(getattr(type(base_instance), k))]


def extract_properties_option_from_class(base_instance, hierarchical_classes: List[str] = []):
    return {k: [calc_internal_extract(base_instance.__getattribute__(k), hierarchical_classes)] for k, v in
            type(base_instance).__dict__.items() if k[:1] != '_' and not callable(getattr(type(base_instance), k))}


def calc_internal_extract(base_instance, hierarchical_classes: List[str]):
    if type(base_instance).__name__ in hierarchical_classes:
        internal_extracted = create_options_class(base_instance, hierarchical_classes)
        return internal_extracted
    return base_instance


def create_options_class(base_instance: object, hierarchical_classes: List[str] = []) -> Options:
    internal_extracted = {'internal_class': type(base_instance)}
    internal_extracted.update(extract_properties_option_from_class(base_instance, hierarchical_classes))
    return type(type(base_instance).__name__ + 'Options', (Options,), internal_extracted)
