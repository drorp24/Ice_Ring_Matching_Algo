import inspect
import sys


def name_to_class(class_name: str, module_name_with_import_class: str):
    return getattr(sys.modules[module_name_with_import_class], class_name)


def get_all_module_class_names_from_globals(module_globals):
    return list(map(lambda item: item[0], filter(lambda item: inspect.isclass(item[1]), module_globals.items())))
