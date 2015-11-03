"""Tests for our GroupMembershipMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import AccountMigrator, DirectoryMigrator, GroupMembershipMigrator, GroupMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class GroupMembershipMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.src_dir = self.src.directories.create({'name': uuid4().hex})
        self.src_group = self.src_dir.groups.create({'name': uuid4().hex})
        self.src_account = self.src_dir.accounts.create({
            'given_name': uuid4().hex,
            'surname': uuid4().hex,
            'email': uuid4().hex + '@test.com',
            'password': self.random_password(),
        })
        self.src_membership = self.src_account.add_group(self.src_group)

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.src_dir)
        self.dst_dir = migrator.migrate()

        migrator = GroupMigrator(destination_directory=self.dst_dir, source_group=self.src_group)
        self.dst_group = migrator.migrate()

        migrator = AccountMigrator(destination_directory=self.dst_dir, source_account=self.src_account, source_password=self.random_password())
        self.dst_account = migrator.migrate()

    def tearDown(self):
        self.src_dir.delete()
        self.dst_dir.delete()

    def random_password(self):
        return uuid4().hex + uuid4().hex.upper() + '!'

    def test_get_destination_account(self):
        migrator = GroupMembershipMigrator(destination_client=self.dst, source_group_membership=self.src_membership)
        account = migrator.get_destination_account()

        self.assertEqual(account.href, self.dst_account.href)
        self.assertEqual(account.email, self.dst_account.email)

    def test_get_destination_group(self):
        migrator = GroupMembershipMigrator(destination_client=self.dst, source_group_membership=self.src_membership)
        group = migrator.get_destination_group()

        self.assertEqual(group.href, self.dst_group.href)
        self.assertEqual(group.name, self.dst_group.name)

    def test_copy_membership(self):
        migrator = GroupMembershipMigrator(destination_client=self.dst, source_group_membership=self.src_membership)
        membership = migrator.copy_membership()

        self.assertEqual(membership.group.name, self.src_membership.group.name)
        self.assertEqual(membership.group.description, self.src_membership.group.description)
        self.assertEqual(membership.account.username, self.src_membership.account.username)
        self.assertEqual(membership.account.email, self.src_membership.account.email)

    def test_migrate(self):
        migrator = GroupMembershipMigrator(destination_client=self.dst, source_group_membership=self.src_membership)
        membership = migrator.migrate()

        self.assertEqual(membership.group.name, self.src_membership.group.name)
        self.assertEqual(membership.group.description, self.src_membership.group.description)
        self.assertEqual(membership.account.username, self.src_membership.account.username)
        self.assertEqual(membership.account.email, self.src_membership.account.email)
