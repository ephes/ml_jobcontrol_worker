# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
    # hush pyflakes
    setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='ml_jobcontrol_worker',
    version='0.0.1',
    author='Jochen Wersdörfer',
    author_email='jochen-mljobcontrol@wersdoerfer.de',
    include_package_data=True,
    install_requires = ['requests>=0.14.0'],
    py_modules=['ml_jobcontrol'],
    url='https://github.com/ephes/ml_jobcontrol_worker',
    license='BSD licence, see LICENCE.txt',
    description='Get jobs from ml_jobcontrol and submit results',
    long_description=open('README.md').read(),
)
