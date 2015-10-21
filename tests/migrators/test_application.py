"""Tests for our ApplicationMigrator class."""


from datetime import timedelta
from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import ApplicationMigrator
from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class ApplicationMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.app = self.src.applications.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
            'status': 'DISABLED',
            'custom_data': {'hi': 'there'},
        })
        oauth_policy = self.app.oauth_policy
        oauth_policy.access_token_ttl = timedelta(hours=2)
        oauth_policy.refresh_token_ttl = timedelta(hours=24)
        oauth_policy.save()

    def tearDown(self):
        self.app.delete()

    def test_get_custom_data(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        custom_data = migrator.get_custom_data()
        self.assertTrue(custom_data)
        self.assertEqual(custom_data['hi'], 'there')

    def test_get_oauth_policy(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        oauth_policy = migrator.get_oauth_policy()
        self.assertTrue(oauth_policy)
        self.assertEqual(oauth_policy.access_token_ttl, timedelta(hours=2))
        self.assertEqual(oauth_policy.refresh_token_ttl, timedelta(hours=24))

    def test_copy_app(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        copied_app = migrator.copy_app()

        self.assertEqual(copied_app.description, self.app.description)
        self.assertEqual(copied_app.name, self.app.name)
        self.assertEqual(copied_app.status, self.app.status)

        copied_app.delete()

    def test_copy_custom_data(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        copied_app = migrator.copy_app()
        copied_data = migrator.copy_custom_data()

        self.assertEqual(copied_data['hi'], 'there')
        copied_app.delete()

    def test_copy_oauth_policy(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        copied_app = migrator.copy_app()
        copied_policy = migrator.copy_oauth_policy()

        self.assertEqual(copied_policy.access_token_ttl, timedelta(hours=2))
        self.assertEqual(copied_policy.refresh_token_ttl, timedelta(hours=24))
        copied_app.delete()

    def test_migrate(self):
        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.app)
        copied_app = migrator.migrate()
        copied_data = copied_app.custom_data
        copied_policy = copied_app.oauth_policy

        self.assertEqual(copied_app.description, self.app.description)
        self.assertEqual(copied_app.name, self.app.name)
        self.assertEqual(copied_app.status, self.app.status)
        self.assertEqual(copied_data['hi'], 'there')
        self.assertEqual(copied_policy.access_token_ttl, timedelta(hours=2))
        self.assertEqual(copied_policy.refresh_token_ttl, timedelta(hours=24))

        copied_app.delete()
