"""Tests for our DirectoryMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import DirectoryMigrator
from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class DirectoryMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

    def test_get_custom_data(self):
        dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        custom_data = migrator.get_custom_data()
        self.assertTrue(custom_data)
        self.assertEqual(custom_data['hi'], 'there')

        dir.delete()

    def test_get_strength(self):
        dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        strength = migrator.get_strength()
        self.assertTrue(strength)

        dir.delete()

    def test_copy_dir(self):
        dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        copied_dir = migrator.copy_dir()

        self.assertTrue(copied_dir)
        self.assertEqual(dir.description, copied_dir.description)
        self.assertEqual(dir.name, copied_dir.name)
        self.assertEqual(dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(dir.status, copied_dir.status)

        dir.delete()
        copied_dir.delete()

        dir = self.src.directories.create({
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

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        copied_dir = migrator.copy_dir()

        self.assertTrue(copied_dir)
        self.assertEqual(dir.description, copied_dir.description)
        self.assertEqual(dir.name, copied_dir.name)
        self.assertEqual(dir.provider.provider_id, copied_dir.provider.provider_id)
        self.assertEqual(dir.provider.client_id, copied_dir.provider.client_id)
        self.assertEqual(dir.provider.client_secret, copied_dir.provider.client_secret)
        self.assertEqual(dir.provider.redirect_uri, copied_dir.provider.redirect_uri)
        self.assertEqual(dir.status, copied_dir.status)

        dir.delete()
        copied_dir.delete()

    def test_copy_custom_data(self):
        dir = self.src.directories.create({
            'custom_data': {'hi': 'there'},
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        copied_dir = migrator.copy_dir()
        copied_data = migrator.copy_custom_data()

        self.assertEqual(copied_data['hi'], 'there')

        dir.delete()
        copied_dir.delete()

    def test_copy_strength(self):
        dir = self.src.directories.create({'name': uuid4().hex})
        strength = dir.password_policy.strength

        strength.max_length = 101
        strength.save()

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        copied_dir = migrator.copy_dir()
        copied_strength = migrator.copy_strength()

        for key in copied_strength.writable_attrs:
            self.assertEqual(copied_strength[key], strength[key])

        dir.delete()
        copied_dir.delete()

    def test_migrate(self):
        dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })

        custom_data = dir.custom_data
        strength = dir.password_policy.strength

        strength.max_length = 100
        strength.min_length = 1
        strength.min_lower_case = 0
        strength.min_numeric = 0
        strength.min_symbol = 0
        strength.min_upper_case = 0
        strength.min_diacritic = 0
        strength.save()

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=dir)
        copied_dir = migrator.migrate()
        copied_custom_data = copied_dir.custom_data
        copied_strength = copied_dir.password_policy.strength

        self.assertEqual(copied_dir.description, dir.description)
        self.assertEqual(copied_dir.name, dir.name)
        self.assertEqual(copied_dir.status, dir.status)

        self.assertEqual(copied_custom_data['hi'], custom_data['hi'])

        for key in sanitize(strength).keys():
            self.assertEqual(copied_strength[key], strength[key])

        dir.delete()
        copied_dir.delete()
