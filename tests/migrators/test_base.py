"""Tests for our BaseMigrator class."""


from os import environ
from unittest import TestCase

from migrate.migrators import BaseMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class BaseMigratorTest(TestCase):
    def setUp(self):
        self.src = 'blah'
        self.dst = 'blah'

    def test_init(self):
        migrator = BaseMigrator(self.src, self.dst)
        self.assertEqual(migrator.src, self.src)
        self.assertEqual(migrator.dst, self.dst)
        self.assertEqual(migrator.from_date, None)
        self.assertEqual(migrator.verbose, False)

        migrator = BaseMigrator(self.src, self.dst, verbose=True)
        self.assertEqual(migrator.verbose, True)

    def test_repr(self):
        migrator = BaseMigrator(self.src, self.dst)
        self.assertEqual('BaseMigrator()', migrator.__repr__())
