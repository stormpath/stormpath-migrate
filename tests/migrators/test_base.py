"""Tests for our BaseMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import BaseMigrator, DirectoryMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class BaseMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

    def test_init(self):
        migrator = BaseMigrator(self.src, self.dst, passwords='hi.txt')
        self.assertEqual(migrator.src, self.src)
        self.assertEqual(migrator.dst, self.dst)
        self.assertEqual(migrator.from_date, None)
        self.assertEqual(migrator.verbose, False)

        migrator = BaseMigrator(self.src, self.dst, passwords='hi.txt', verbose=True)
        self.assertEqual(migrator.verbose, True)

    def test_repr(self):
        migrator = BaseMigrator(self.src, self.dst, passwords='hi.txt')
        self.assertEqual('BaseMigrator()', migrator.__repr__())
