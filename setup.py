from setuptools import setup, find_packages, Extension, Feature

with open('README.txt', 'r') as readme:
    README_TEXT = readme.read()

setup(
    name='erinyes',
    version='0.1a',
    author='Ioannis Tziakos',
    description='Testing tools',
    long_description=README_TEXT,
    requires=['psutil'],
    install_requires=['distribute'],
    packages=find_packages(),
    test_suite='erinyes.tests')