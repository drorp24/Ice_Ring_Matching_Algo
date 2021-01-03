import sys


def name_to_class(class_name: str, local_name: str):
    return getattr(sys.modules[local_name], class_name)
