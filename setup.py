# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ElDomadorBot',
    version='0.1.0',
    description='Bot para ElDomador',
    long_description=readme,
    author='Edgardo Garcia Hoeffler',
    author_email='snopler@gmail.com',
    url='https://github.com/snopler/ElDomadorBot',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

