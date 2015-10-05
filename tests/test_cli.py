"""Our CLI tests."""


from os import environ
from unittest import TestCase

from stormpath.client import Client

from migrate.cli import create_clients, validate_credentials


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class CreateClientsTest(TestCase):
    def test_returns_two_clients(self):
        self.assertEqual(len(create_clients(SRC_CLIENT_ID + ':' + SRC_CLIENT_SECRET, DST_CLIENT_ID + ':' + DST_CLIENT_SECRET)), 2)

    def test_returns_client_objects(self):
        clients = create_clients(SRC_CLIENT_ID + ':' + SRC_CLIENT_SECRET, DST_CLIENT_ID + ':' + DST_CLIENT_SECRET)
        self.assertIsInstance(clients[0], Client)
        self.assertIsInstance(clients[1], Client)


class ValidateCredentialsTest(TestCase):
    def test_raises_error_on_invalid_credentials(self):
        with self.assertRaises(ValueError):
            validate_credentials('hi', 'there')

        with self.assertRaises(ValueError):
            validate_credentials(':secret', 'xxx:yyy')

    def test_works_with_valid_credentials(self):
        validate_credentials(SRC_CLIENT_ID + ':' + SRC_CLIENT_SECRET, DST_CLIENT_ID + ':' + DST_CLIENT_SECRET)
