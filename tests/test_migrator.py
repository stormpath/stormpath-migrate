"""Tests for our Migrator class."""


from unittest import TestCase

from migrate.migrator import Migrator


class MigratorTest(TestCase):
    def test_init(self):
        migrator = Migrator('id:secret', 'xxx:yyy')
        self.assertEqual(migrator.src, 'id:secret')
        self.assertEqual(migrator.dst, 'xxx:yyy')
        self.assertEqual(migrator.from_date, None)

    def test_repr(self):
        migrator = Migrator('id:secret', 'xxx:yyy')
        self.assertTrue('id:secret' in migrator.__repr__())
        self.assertTrue('xxx:yyy' in migrator.__repr__())
