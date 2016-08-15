"""Tests for our GroupMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import DirectoryMigrator, GroupMigrator
from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class GroupMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
        })

        self.group = self.dir.groups.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.dir)
        self.dst_dir = migrator.migrate()

    def tearDown(self):
        self.dir.delete()
        self.dst_dir.delete()

    def test_copy_group(self):
        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.group)
        migrator.destination_group = migrator.get_destination_group()
        migrator.get_destination_group()
        copied_group = migrator.copy_group()

        self.assertTrue(copied_group)
        self.assertEqual(copied_group.description, self.group.description)
        self.assertEqual(copied_group.name, self.group.name)
        self.assertEqual(copied_group.status, self.group.status)

    def test_copy_custom_data(self):
        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.group)
        migrator.destination_group = migrator.get_destination_group()
        copied_group = migrator.copy_group()
        copied_custom_data = migrator.copy_custom_data()

        self.assertEqual(copied_custom_data['hi'], 'there')

    def test_migrate(self):
        custom_data = self.group.custom_data

        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.group)
        copied_group = migrator.migrate()
        copied_custom_data = copied_group.custom_data

        self.assertEqual(copied_group.description, self.group.description)
        self.assertEqual(copied_group.name, self.group.name)
        self.assertEqual(copied_group.status, self.group.status)
        self.assertEqual(copied_custom_data['hi'], self.group.custom_data['hi'])
