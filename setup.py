import os
import sys

from setuptools import setup
from setuptools.command.test import test

# Get the long description from the README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class PyTest(test):
    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(['tests'])
        sys.exit(errno)


setup(
    name='dftlib',
    version='0.1',
    author='M. Volk',
    author_email='matthias.volk@cs.rwth-aachen.de',
    maintainer='M. Volk',
    maintainer_email='matthias.volk@cs.rwth-aachen.de',
    url='http://moves.rwth-aachen.de',
    description='dftlib - Python library for dynamic fault tree analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['dftlib'],
    cmdclass={
        'test': PyTest
    },
    zip_safe=False,
    install_requires=[],
    extras_require={
        'with_smt': ['z3'],
        'with_stormpy': ['stormpy']
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    python_requires='>=3',
)
