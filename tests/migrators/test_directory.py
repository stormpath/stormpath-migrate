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

    def test_get_strength(self):
        directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(directory.href)
        src_strength = migrator.get_strength(src_dir)

        self.assertTrue(src_strength)

        directory.delete()

    def test_copy_dir(self):
        directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(directory.href)
        copied_dir = migrator.copy_dir(dir=src_dir)

        self.assertTrue(copied_dir)
        self.assertEqual(src_dir.description, copied_dir.description)
        self.assertEqual(src_dir.name, copied_dir.name)
        self.assertEqual(src_dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(src_dir.status, copied_dir.status)

        directory.delete()
        copied_dir.delete()

        directory = self.src.directories.create({
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

        src_dir = migrator.get_resource(directory.href)
        copied_dir = migrator.copy_dir(dir=src_dir)

        self.assertTrue(copied_dir)
        self.assertEqual(src_dir.description, copied_dir.description)
        self.assertEqual(src_dir.name, copied_dir.name)
        self.assertEqual(src_dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(src_dir.provider.client_id, copied_dir.provider.client_id)
        self.assertEqual(src_dir.provider.client_secret, copied_dir.provider.client_secret)
        self.assertEqual(src_dir.provider.redirect_uri, copied_dir.provider.redirect_uri)
        self.assertEqual(src_dir.status, copied_dir.status)

        directory.delete()
        copied_dir.delete()

    def test_copy_strength(self):
        directory = self.src.directories.create({'name': uuid4().hex})
        migrator = DirectoryMigrator(self.src, self.dst)

        src_dir = migrator.get_resource(directory.href)
        strength = migrator.get_strength(src_dir)
        copied_dir = migrator.copy_dir(dir=src_dir)
        copied_strength = migrator.copy_strength(dir=src_dir, strength=strength)

        for key in strength.writable_attrs:
            self.assertEqual(copied_strength[key], strength[key])

        directory.delete()
        copied_dir.delete()

    def test_migrate(self):
        directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        custom_data = directory.custom_data

        strength = directory.password_policy.strength
        strength.max_length = 100
        strength.min_length = 1
        strength.min_lower_case = 0
        strength.min_numeric = 0
        strength.min_symbol = 0
        strength.min_upper_case = 0
        strength.min_diacritic = 0
        strength.save()

        migrator = DirectoryMigrator(self.src, self.dst)

        copied_dir = migrator.copy_dir(dir=directory)
        copied_custom_data = migrator.copy_custom_data(resource=directory, custom_data=custom_data)
        copied_strength = migrator.copy_strength(dir=directory, strength=strength)

        self.assertEqual(copied_dir.description, directory.description)
        self.assertEqual(copied_dir.name, directory.name)
        self.assertEqual(copied_dir.status, directory.status)

        self.assertEqual(copied_custom_data['hi'], custom_data['hi'])

        for key in dict(strength).keys():
            self.assertEqual(copied_strength[key], strength[key])

        directory.delete()
        copied_dir.delete()
