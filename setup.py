"""Packaging settings."""


from codecs import open
from os.path import abspath, dirname, join

from setuptools import find_packages, setup


this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
    long_description = file.read()


setup(
    name = 'stormpath-migrate',
    version = '1.0.0',
    description = 'Migrate a Stormpath tenant from one place to another.',
    long_description = long_description,
    url = 'https://github.com/rdegges/stormpath-migrate',
    author = 'Randall Degges',
    author_email = 'r@rdegges.com',
    license = 'UNLICENSE',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords = 'stormpath authentication migration development',
    packages = find_packages(exclude=['tests*']),
    install_requires = ['docopt', 'stormpath'],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require = {
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points = {
        'console_scripts': [
            'stormpath-migrate=migrate.cli:main',
        ],
    },
)
