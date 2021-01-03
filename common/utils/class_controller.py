import sys


def name_to_class(class_name):
    return getattr(sys.modules[__name__], class_name)
