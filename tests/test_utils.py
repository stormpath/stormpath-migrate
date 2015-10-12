"""Our utility tests."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']


class SanitizeTest(TestCase):
    def setUp(self):
        self.client = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.directory = self.client.directories.create({'name': uuid4().hex})

    def tearDown(self):
        self.directory.delete()

    def test_removes_fields(self):
        obj = sanitize(self.directory.provider)
        self.assertFalse(obj.get('href'))
        self.assertFalse(obj.get('created_at'))
        self.assertFalse(obj.get('modified_at'))
