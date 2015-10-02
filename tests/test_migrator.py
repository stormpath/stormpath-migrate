"""Tests for our Migrator class."""


from unittest import TestCase

from migrate.migrator import Migrator


class MigratorTest(TestCase):
    def test_init_stores_properties(self):
        migrator = Migrator('id:secret', 'xxx:yyy')
        self.assertEqual(migrator.src, 'id:secret')
        self.assertEqual(migrator.dst, 'xxx:yyy')
        self.assertEqual(migrator.from_date, None)
