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

    def test_get_src_dir(self):
        self.directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'ENABLED',
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        self.assertTrue(migrator.get_src_dir(self.directory.href))
        self.assertEqual(migrator.src_dir.href, self.directory.href)
        self.assertEqual(migrator.src_dir.name, self.directory.name)

    def test_create_dst_dir(self):
        self.directory = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
        })

        migrator = DirectoryMigrator(self.src, self.dst)

        migrator.get_src_dir(self.directory.href)
        self.assertTrue(migrator.create_dst_dir())
        self.assertEqual(migrator.src_dir.description, migrator.dst_dir.description)
        self.assertEqual(migrator.src_dir.name, migrator.dst_dir.name)
        self.assertEqual(migrator.src_dir.provider.provider_id, migrator.dst_dir.provider.provider_id)
        self.assertEqual(migrator.src_dir.status, migrator.dst_dir.status)

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

        migrator.get_src_dir(self.directory.href)
        self.assertTrue(migrator.create_dst_dir())
        self.assertEqual(migrator.src_dir.description, migrator.dst_dir.description)
        self.assertEqual(migrator.src_dir.name, migrator.dst_dir.name)
        self.assertEqual(migrator.src_dir.provider.provider_id, migrator.dst_dir.provider.provider_id)
        self.assertEqual(migrator.src_dir.provider.client_id, migrator.dst_dir.provider.client_id)
        self.assertEqual(migrator.src_dir.provider.client_secret, migrator.dst_dir.provider.client_secret)
        self.assertEqual(migrator.src_dir.provider.redirect_uri, migrator.dst_dir.provider.redirect_uri)
        self.assertEqual(migrator.src_dir.status, migrator.dst_dir.status)
