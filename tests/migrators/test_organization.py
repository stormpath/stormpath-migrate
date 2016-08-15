"""Tests for our OrganizationMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import OrganizationMigrator
from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class OrganizationMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)
        self.org = self.src.organizations.create({
            'custom_data': {'hi': 'there'},
            'description': uuid4().hex,
            'name': uuid4().hex,
            'name_key': uuid4().hex,
            'status': 'DISABLED',
        })
        self.dst_org = None

    def tearDown(self):
        self.org.delete()
        if self.dst_org:
            self.dst_org.delete()

    def test_copy_org_organization(self):
        migrator = OrganizationMigrator(destination_client=self.dst, source_organization=self.org)
        copied_org = migrator.copy_organization()

        self.assertEqual(copied_org.description, self.org.description)
        self.assertEqual(copied_org.name, self.org.name)
        self.assertEqual(copied_org.name_key, self.org.name_key)
        self.assertEqual(copied_org.status, self.org.status)

    def test_copy_custom_data(self):
        migrator = OrganizationMigrator(destination_client=self.dst, source_organization=self.org)
        migrator.copy_organization()
        copied_data = migrator.copy_custom_data()
        self.assertEqual(copied_data['hi'], 'there')

    def test_migrate(self):
        migrator = OrganizationMigrator(destination_client=self.dst, source_organization=self.org)
        copied_org = migrator.migrate()
        copied_custom_data = copied_org.custom_data

        self.assertEqual(copied_org.description, self.org.description)
        self.assertEqual(copied_org.name, self.org.name)
        self.assertEqual(copied_org.name_key, self.org.name_key)
        self.assertEqual(copied_org.status, self.org.status)
        self.assertEqual(copied_custom_data['hi'], 'there')
