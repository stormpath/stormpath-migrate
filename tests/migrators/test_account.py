"""Tests for our AccountMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import AccountMigrator, DirectoryMigrator


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class AccountMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.dir = self.src.directories.create({
            'description': uuid4().hex,
            'name': uuid4().hex,
        })

        self.account = self.dir.accounts.create({
            'custom_data': {'hi': 'there'},
            'username': uuid4().hex,
            'given_name': uuid4().hex,
            'middle_name': uuid4().hex,
            'surname': uuid4().hex,
            'email': uuid4().hex + '@test.com',
            'password': '$2a$13$7nOY.0Y9BmFUx77cT/3bZO8rTSDbi0a1JPHdzqyp6YexrNTYKZbQ2',
            'status': 'ENABLED',
        })

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.dir)
        self.dst_dir = migrator.migrate()

    def tearDown(self):
        self.dir.delete()
        self.dst_dir.delete()

    def test_copy_account(self):
        migrator = AccountMigrator(
            destination_directory = self.dst_dir,
            source_account = self.account,
            source_password = '$2a$13$7nOY.0Y9BmFUx77cT/3bZO8rTSDbi0a1JPHdzqyp6YexrNTYKZbQ2',
        )
        copied_account = migrator.copy_account()

        self.assertEqual(copied_account.username, self.account.username)
        self.assertEqual(copied_account.given_name, self.account.given_name)
        self.assertEqual(copied_account.middle_name, self.account.middle_name)
        self.assertEqual(copied_account.surname, self.account.surname)
        self.assertEqual(copied_account.email, self.account.email)
        self.assertEqual(copied_account.status, self.account.status)

    def test_copy_custom_data(self):
        migrator = AccountMigrator(
            destination_directory = self.dst_dir,
            source_account = self.account,
            source_password = '$2a$13$7nOY.0Y9BmFUx77cT/3bZO8rTSDbi0a1JPHdzqyp6YexrNTYKZbQ2',
        )
        migrator.copy_account()
        copied_data = migrator.copy_custom_data()

        self.assertEqual(copied_data['hi'], 'there')

    def test_migrate(self):
        migrator = AccountMigrator(
            destination_directory = self.dst_dir,
            source_account = self.account,
            source_password = '$2a$13$7nOY.0Y9BmFUx77cT/3bZO8rTSDbi0a1JPHdzqyp6YexrNTYKZbQ2',
        )

        copied_account = migrator.migrate()
        copied_custom_data = copied_account.custom_data

        self.assertEqual(copied_account.username, self.account.username)
        self.assertEqual(copied_account.given_name, self.account.given_name)
        self.assertEqual(copied_account.middle_name, self.account.middle_name)
        self.assertEqual(copied_account.surname, self.account.surname)
        self.assertEqual(copied_account.email, self.account.email)
        self.assertEqual(copied_account.status, self.account.status)
        self.assertEqual(copied_custom_data['hi'], 'there')
