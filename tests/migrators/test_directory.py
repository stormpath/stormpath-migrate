"""Tests for our DirectoryMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import DirectoryMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class DirectoryMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

    def tearDown(self):
        self.directory.delete()

    def test_get_strength(self):
        self.directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(self.directory.href)
        src_strength = migrator.get_strength(src_dir)

        self.assertTrue(src_strength)

    def test_copy_dir(self):
        self.directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(self.directory.href)
        custom_data = migrator.get_custom_data(src_dir)
        strength = migrator.get_strength(src_dir)
        copied_dir = migrator.copy_dir(dir=src_dir, custom_data=custom_data, strength=strength)

        self.assertTrue(copied_dir)
        self.assertEqual(src_dir.description, copied_dir.description)
        self.assertEqual(src_dir.name, copied_dir.name)
        self.assertEqual(src_dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(src_dir.status, copied_dir.status)
        self.assertEqual(src_dir.status, copied_dir.status)
        self.assertEqual(src_dir.custom_data['hi'], copied_dir.custom_data['hi'])
        self.assertEqual(strength.min_lower_case, copied_dir.password_policy.strength.min_lower_case)

        self.directory.delete()

        self.directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'provider': {
                'provider_id': 'google',
                'client_id': 'test',
                'client_secret': 'test',
                'redirect_uri': 'https://test.com/callback',
            }
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(self.directory.href)
        custom_data = migrator.get_custom_data(src_dir)
        strength = migrator.get_strength(src_dir)
        copied_dir = migrator.copy_dir(dir=src_dir, custom_data=custom_data, strength=strength)

        self.assertTrue(copied_dir)
        self.assertEqual(src_dir.description, copied_dir.description)
        self.assertEqual(src_dir.name, copied_dir.name)
        self.assertEqual(src_dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(src_dir.provider.client_id, copied_dir.provider.client_id)
        self.assertEqual(src_dir.provider.client_secret, copied_dir.provider.client_secret)
        self.assertEqual(src_dir.provider.redirect_uri, copied_dir.provider.redirect_uri)
        self.assertEqual(src_dir.status, copied_dir.status)
        self.assertEqual(src_dir.status, copied_dir.status)
        self.assertEqual(strength.min_lower_case, copied_dir.password_policy.strength.min_lower_case)
