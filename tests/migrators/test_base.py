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
        self.src = '%s:%s' % (SRC_CLIENT_ID, SRC_CLIENT_SECRET)
        self.dst = '%s:%s' % (DST_CLIENT_ID, DST_CLIENT_SECRET)

    def test_init(self):
        migrator = BaseMigrator('id:secret', 'xxx:yyy')
        self.assertEqual(migrator.src, 'id:secret')
        self.assertEqual(migrator.dst, 'xxx:yyy')
        self.assertEqual(migrator.from_date, None)

    def test_repr(self):
        migrator = BaseMigrator('id:secret', 'xxx:yyy')
        self.assertTrue('id:secret' in migrator.__repr__())
        self.assertTrue('xxx:yyy' in migrator.__repr__())

    def test_validate_credentials(self):
        with self.assertRaises(ValueError):
            BaseMigrator('hi', 'there')

        with self.assertRaises(ValueError):
            BaseMigrator(':secret', 'xxx:yyy')

    def test_create_clients(self):
        migrator = BaseMigrator(self.src, self.dst)
        migrator._create_clients()
        self.assertTrue(migrator.src_client)
        self.assertTrue(migrator.dst_client)
