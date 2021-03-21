import os

from setuptools import setup, find_packages

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_file = 'requirements.txt'
full_path = '/'.join([lib_folder, requirement_file])

install_requires = []
if os.path.isfile(full_path):
    with open(full_path) as f:
        install_requires = f.read().splitlines()

setup(name='MatchingAlgorithms',
      version='0.1.0',
      description='',
      install_requires=install_requires,
      build_requires=['Cython'],
      author='',
      packages=find_packages())
