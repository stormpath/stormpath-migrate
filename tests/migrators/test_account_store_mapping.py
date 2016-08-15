"""Tests for our ApplicationAccountStoreMappingMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import ApplicationMigrator, ApplicationAccountStoreMappingMigrator, DirectoryMigrator, GroupMigrator, OrganizationAccountStoreMappingMigrator, OrganizationMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class ApplicationAccountStoreMappingMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.src_app = self.src.applications.create({'name': uuid4().hex})
        self.src_dir = self.src.directories.create({'name': uuid4().hex})
        self.src_org = self.src.organizations.create({'name': uuid4().hex, 'name_key': uuid4().hex})
        self.src_group = self.src_dir.groups.create({'name': uuid4().hex})

        migrator = ApplicationMigrator(destination_client=self.dst, source_application=self.src_app)
        self.dst_app = migrator.migrate()

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.src_dir)
        self.dst_dir = migrator.migrate()

        migrator = OrganizationMigrator(destination_client=self.dst, source_organization=self.src_org)
        self.dst_org = migrator.migrate()

        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.src_group)
        self.dst_group = migrator.migrate()

        self.src_mapping_1 = self.src_app.account_store_mappings.create({
            'application': self.src_app,
            'account_store': self.src_dir,
            'list_index': 0,
            'is_default_account_store': True,
            'is_default_group_store': True,
        })

        self.src_mapping_2 = self.src_app.account_store_mappings.create({
            'application': self.src_app,
            'account_store': self.src_org,
            'list_index': 1,
            'is_default_account_store': False,
            'is_default_group_store': False,
        })

        self.src_mapping_3 = self.src_app.account_store_mappings.create({
            'application': self.src_app,
            'account_store': self.src_group,
            'list_index': 2,
            'is_default_account_store': False,
            'is_default_group_store': False,
        })

    def tearDown(self):
        self.src_app.delete()
        self.src_dir.delete()
        self.src_org.delete()

        self.dst_app.delete()
        self.dst_dir.delete()
        self.dst_org.delete()

    def test_get_destination_account_store(self):
        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.src_app, source_account_store_mapping=self.src_mapping_1)
        migrator.get_source_account_store()
        account_store = migrator.get_destination_account_store()
        self.assertEqual(account_store.name, self.dst_dir.name)
        self.assertEqual(account_store.description, self.dst_dir.description)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.src_app, source_account_store_mapping=self.src_mapping_2)
        migrator.get_source_account_store()
        account_store = migrator.get_destination_account_store()
        self.assertEqual(account_store.name, self.dst_org.name)
        self.assertEqual(account_store.description, self.dst_org.description)
        self.assertEqual(account_store.name_key, self.dst_org.name_key)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.src_app, source_account_store_mapping=self.src_mapping_3)
        migrator.get_source_account_store()
        account_store = migrator.get_destination_account_store()
        self.assertEqual(account_store.name, self.dst_group.name)
        self.assertEqual(account_store.description, self.dst_group.description)

    def test_copy_mapping(self):
        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_1)
        migrator.destination_tenant = migrator.destination_application.tenant
        migrator.source_account_store = migrator.source_account_store_mapping.account_store
        migrator.destination_account_store = migrator.get_destination_account_store()
        dst_mapping = migrator.copy_mapping()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_dir.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_dir.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_1.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_1.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_1.is_default_group_store)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_2)
        dst_mapping = migrator.copy_mapping()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_org.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_2.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_2.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_2.is_default_group_store)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_3)
        dst_mapping = migrator.copy_mapping()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_group.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_group.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_3.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_3.is_default_account_store)

    def test_migrate(self):
        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_1)
        dst_mapping = migrator.migrate()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_dir.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_dir.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_1.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_1.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_1.is_default_group_store)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_2)
        dst_mapping = migrator.migrate()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_org.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_2.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_2.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_2.is_default_group_store)

        migrator = ApplicationAccountStoreMappingMigrator(destination_application=self.dst_app, source_account_store_mapping=self.src_mapping_3)
        dst_mapping = migrator.migrate()
        self.assertEqual(dst_mapping.application.name, self.src_app.name)
        self.assertEqual(dst_mapping.application.description, self.src_app.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_group.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_group.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_3.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_3.is_default_account_store)


class OrganizationAccountStoreMappingMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.src_dir = self.src.directories.create({'name': uuid4().hex})
        self.src_group = self.src_dir.groups.create({'name': uuid4().hex})
        self.src_org = self.src.organizations.create({'name': uuid4().hex, 'name_key': uuid4().hex})

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.src_dir)
        self.dst_dir = migrator.migrate()

        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.src_group)
        self.dst_group = migrator.migrate()

        migrator = OrganizationMigrator(destination_client=self.dst, source_organization=self.src_org)
        self.dst_org = migrator.migrate()

        self.src_mapping_1 = self.src.organization_account_store_mappings.create({
            'organization': self.src_org,
            'account_store': self.src_dir,
            'list_index': 0,
            'is_default_account_store': True,
            'is_default_group_store': True,
        })

        self.src_mapping_2 = self.src.organization_account_store_mappings.create({
            'organization': self.src_org,
            'account_store': self.src_group,
            'list_index': 1,
            'is_default_account_store': False,
            'is_default_group_store': False,
        })

    def tearDown(self):
        self.src_org.delete()
        self.src_dir.delete()
        self.dst_org.delete()
        self.dst_dir.delete()

    def test_get_source_account_store(self):
        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_1)
        account_store = migrator.get_source_account_store()
        self.assertEqual(account_store.name, self.src_dir.name)
        self.assertEqual(account_store.description, self.src_dir.description)

        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_2)
        account_store = migrator.get_source_account_store()
        account_store = migrator.get_source_account_store()
        self.assertEqual(account_store.name, self.src_group.name)
        self.assertEqual(account_store.description, self.src_group.description)

    def test_get_destination_account_store(self):
        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_1)
        migrator.get_source_account_store()
        account_store = migrator.get_destination_account_store()
        self.assertEqual(account_store.name, self.dst_dir.name)
        self.assertEqual(account_store.description, self.dst_dir.description)

        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_2)
        migrator.get_source_account_store()
        account_store = migrator.get_destination_account_store()
        self.assertEqual(account_store.name, self.dst_group.name)
        self.assertEqual(account_store.description, self.dst_group.description)

    def test_copy_mapping(self):
        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_1)
        dst_mapping = migrator.copy_mapping()
        self.assertEqual(dst_mapping.organization.name, self.src_org.name)
        self.assertEqual(dst_mapping.organization.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.organization.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_dir.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_dir.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_1.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_1.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_1.is_default_group_store)

        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_2)
        dst_mapping = migrator.copy_mapping()
        self.assertEqual(dst_mapping.organization.name, self.src_org.name)
        self.assertEqual(dst_mapping.organization.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.organization.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_group.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_group.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_2.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_2.is_default_account_store)

    def test_migrate(self):
        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_1)
        dst_mapping = migrator.migrate()
        self.assertEqual(dst_mapping.organization.name, self.src_org.name)
        self.assertEqual(dst_mapping.organization.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.organization.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_dir.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_dir.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_1.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_1.is_default_account_store)
        self.assertEqual(dst_mapping.is_default_group_store, self.src_mapping_1.is_default_group_store)

        migrator = OrganizationAccountStoreMappingMigrator(destination_organization=self.dst_org, source_account_store_mapping=self.src_mapping_2)
        dst_mapping = migrator.migrate()
        self.assertEqual(dst_mapping.organization.name, self.src_org.name)
        self.assertEqual(dst_mapping.organization.name_key, self.src_org.name_key)
        self.assertEqual(dst_mapping.organization.description, self.src_org.description)
        self.assertEqual(dst_mapping.account_store.name, self.src_group.name)
        self.assertEqual(dst_mapping.account_store.description, self.src_group.description)
        self.assertEqual(dst_mapping.list_index, self.src_mapping_2.list_index)
        self.assertEqual(dst_mapping.is_default_account_store, self.src_mapping_2.is_default_account_store)
