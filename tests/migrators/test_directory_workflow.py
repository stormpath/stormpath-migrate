"""Tests for our DirectoryWorkflowMigrator class."""


from os import environ
from unittest import TestCase
from uuid import uuid4

from stormpath.client import Client

from migrate.migrators import DirectoryMigrator, DirectoryWorkflowMigrator
from migrate.utils import sanitize


# Necessary environment variables.
SRC_CLIENT_ID = environ['SRC_CLIENT_ID']
SRC_CLIENT_SECRET = environ['SRC_CLIENT_SECRET']
DST_CLIENT_ID = environ['DST_CLIENT_ID']
DST_CLIENT_SECRET = environ['DST_CLIENT_SECRET']


class DirectoryWorkflowMigratorTest(TestCase):
    def setUp(self):
        self.src = Client(id=SRC_CLIENT_ID, secret=SRC_CLIENT_SECRET)
        self.dst = Client(id=DST_CLIENT_ID, secret=DST_CLIENT_SECRET)

        self.src_dir = self.src.directories.create({'name': uuid4().hex})

        self.src_account_creation_policy = self.src_dir.account_creation_policy
        self.src_account_creation_policy.verification_email_status = 'ENABLED'
        self.src_account_creation_policy.verification_success_email_status = 'ENABLED'
        self.src_account_creation_policy.welcome_email_status = 'ENABLED'
        self.src_account_creation_policy.save()

        self.src_password_policy = self.src_dir.password_policy
        self.src_password_policy.reset_email_status = 'ENABLED'
        self.src_password_policy.reset_success_email_status = 'ENABLED'
        self.src_password_policy.reset_token_ttl = 100
        self.src_password_policy.save()

        self.src_verification_email_template = self.src_account_creation_policy.verification_email_templates[0]
        self.src_verification_email_template.description = uuid4().hex
        self.src_verification_email_template.from_email_address = uuid4().hex + '@test.com'
        self.src_verification_email_template.from_name = uuid4().hex
        self.src_verification_email_template.html_body = '${url}' + uuid4().hex
        self.src_verification_email_template.mime_type = 'text/html'
        self.src_verification_email_template.name = uuid4().hex
        self.src_verification_email_template.subject = uuid4().hex
        self.src_verification_email_template.text_body = '${url}' + uuid4().hex
        self.src_verification_email_template.save()

        self.src_verification_success_email_template = self.src_account_creation_policy.verification_success_email_templates[0]
        self.src_verification_success_email_template.description = uuid4().hex
        self.src_verification_success_email_template.from_email_address = uuid4().hex + '@test.com'
        self.src_verification_success_email_template.from_name = uuid4().hex
        self.src_verification_success_email_template.html_body = '${url}' + uuid4().hex
        self.src_verification_success_email_template.mime_type = 'text/html'
        self.src_verification_success_email_template.name = uuid4().hex
        self.src_verification_success_email_template.subject = uuid4().hex
        self.src_verification_success_email_template.text_body = '${url}' + uuid4().hex
        self.src_verification_success_email_template.save()

        self.src_welcome_email_template = self.src_account_creation_policy.welcome_email_templates[0]
        self.src_welcome_email_template.description = uuid4().hex
        self.src_welcome_email_template.from_email_address = uuid4().hex + '@test.com'
        self.src_welcome_email_template.from_name = uuid4().hex
        self.src_welcome_email_template.html_body = '${url}' + uuid4().hex
        self.src_welcome_email_template.mime_type = 'text/html'
        self.src_welcome_email_template.name = uuid4().hex
        self.src_welcome_email_template.subject = uuid4().hex
        self.src_welcome_email_template.text_body = '${url}' + uuid4().hex
        self.src_welcome_email_template.save()

        self.src_reset_email_template = self.src_password_policy.reset_email_templates[0]
        self.src_reset_email_template.description = uuid4().hex
        self.src_reset_email_template.from_email_address = uuid4().hex + '@test.com'
        self.src_reset_email_template.from_name = uuid4().hex
        self.src_reset_email_template.html_body = '${url}' + uuid4().hex
        self.src_reset_email_template.mime_type = 'text/html'
        self.src_reset_email_template.name = uuid4().hex
        self.src_reset_email_template.subject = uuid4().hex
        self.src_reset_email_template.text_body = '${url}' + uuid4().hex
        self.src_reset_email_template.save()

        self.src_reset_success_email_template = self.src_password_policy.reset_success_email_templates[0]
        self.src_reset_success_email_template.description = uuid4().hex
        self.src_reset_success_email_template.from_email_address = uuid4().hex + '@test.com'
        self.src_reset_success_email_template.from_name = uuid4().hex
        self.src_reset_success_email_template.html_body = '${url}' + uuid4().hex
        self.src_reset_success_email_template.mime_type = 'text/html'
        self.src_reset_success_email_template.name = uuid4().hex
        self.src_reset_success_email_template.subject = uuid4().hex
        self.src_reset_success_email_template.text_body = '${url}' + uuid4().hex
        self.src_reset_success_email_template.save()

        migrator = DirectoryMigrator(destination_client=self.dst, source_directory=self.src_dir)
        self.dst_dir = migrator.migrate()

    def tearDown(self):
        self.src_dir.delete()
        self.dst_dir.delete()

    def test_get_verification_email_template(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        template = migrator.get_verification_email_template()

        self.assertEqual(template.description, self.src_verification_email_template.description)
        self.assertEqual(template.from_email_address, self.src_verification_email_template.from_email_address)
        self.assertEqual(template.from_name, self.src_verification_email_template.from_name)
        self.assertEqual(template.html_body, self.src_verification_email_template.html_body)
        self.assertEqual(template.mime_type, self.src_verification_email_template.mime_type)
        self.assertEqual(template.name, self.src_verification_email_template.name)
        self.assertEqual(template.subject, self.src_verification_email_template.subject)
        self.assertEqual(template.text_body, self.src_verification_email_template.text_body)

    def test_get_verification_success_email_template(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        template = migrator.get_verification_success_email_template()

        self.assertEqual(template.description, self.src_verification_success_email_template.description)
        self.assertEqual(template.from_email_address, self.src_verification_success_email_template.from_email_address)
        self.assertEqual(template.from_name, self.src_verification_success_email_template.from_name)
        self.assertEqual(template.html_body, self.src_verification_success_email_template.html_body)
        self.assertEqual(template.mime_type, self.src_verification_success_email_template.mime_type)
        self.assertEqual(template.name, self.src_verification_success_email_template.name)
        self.assertEqual(template.subject, self.src_verification_success_email_template.subject)
        self.assertEqual(template.text_body, self.src_verification_success_email_template.text_body)

    def test_get_welcome_email_template(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        template = migrator.get_welcome_email_template()

        self.assertEqual(template.description, self.src_welcome_email_template.description)
        self.assertEqual(template.from_email_address, self.src_welcome_email_template.from_email_address)
        self.assertEqual(template.from_name, self.src_welcome_email_template.from_name)
        self.assertEqual(template.html_body, self.src_welcome_email_template.html_body)
        self.assertEqual(template.mime_type, self.src_welcome_email_template.mime_type)
        self.assertEqual(template.name, self.src_welcome_email_template.name)
        self.assertEqual(template.subject, self.src_welcome_email_template.subject)
        self.assertEqual(template.text_body, self.src_welcome_email_template.text_body)

    def test_get_reset_email_template(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        template = migrator.get_reset_email_template()

        self.assertEqual(template.description, self.src_reset_email_template.description)
        self.assertEqual(template.from_email_address, self.src_reset_email_template.from_email_address)
        self.assertEqual(template.from_name, self.src_reset_email_template.from_name)
        self.assertEqual(template.html_body, self.src_reset_email_template.html_body)
        self.assertEqual(template.mime_type, self.src_reset_email_template.mime_type)
        self.assertEqual(template.name, self.src_reset_email_template.name)
        self.assertEqual(template.subject, self.src_reset_email_template.subject)
        self.assertEqual(template.text_body, self.src_reset_email_template.text_body)

    def test_get_reset_success_email_template(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        template = migrator.get_reset_success_email_template()

        self.assertEqual(template.description, self.src_reset_success_email_template.description)
        self.assertEqual(template.from_email_address, self.src_reset_success_email_template.from_email_address)
        self.assertEqual(template.from_name, self.src_reset_success_email_template.from_name)
        self.assertEqual(template.html_body, self.src_reset_success_email_template.html_body)
        self.assertEqual(template.mime_type, self.src_reset_success_email_template.mime_type)
        self.assertEqual(template.name, self.src_reset_success_email_template.name)
        self.assertEqual(template.subject, self.src_reset_success_email_template.subject)
        self.assertEqual(template.text_body, self.src_reset_success_email_template.text_body)

    def test_copy_workflow(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        directory = migrator.copy_workflow()

        self.assertEqual(directory.account_creation_policy.verification_email_status, self.src_dir.account_creation_policy.verification_email_status)
        self.assertEqual(directory.account_creation_policy.verification_success_email_status, self.src_dir.account_creation_policy.verification_success_email_status)
        self.assertEqual(directory.account_creation_policy.welcome_email_status, self.src_dir.account_creation_policy.welcome_email_status)

        self.assertEqual(directory.password_policy.reset_email_status, self.src_dir.password_policy.reset_email_status)
        self.assertEqual(directory.password_policy.reset_success_email_status, self.src_dir.password_policy.reset_success_email_status)
        self.assertEqual(directory.password_policy.reset_token_ttl, self.src_dir.password_policy.reset_token_ttl)

        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].description, self.src_verification_email_template.description)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].from_email_address, self.src_verification_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].from_name, self.src_verification_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].html_body, self.src_verification_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].mime_type, self.src_verification_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].name, self.src_verification_email_template.name)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].subject, self.src_verification_email_template.subject)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].text_body, self.src_verification_email_template.text_body)

        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].description, self.src_verification_success_email_template.description)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].from_email_address, self.src_verification_success_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].from_name, self.src_verification_success_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].html_body, self.src_verification_success_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].mime_type, self.src_verification_success_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].name, self.src_verification_success_email_template.name)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].subject, self.src_verification_success_email_template.subject)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].text_body, self.src_verification_success_email_template.text_body)

        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].description, self.src_welcome_email_template.description)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].from_email_address, self.src_welcome_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].from_name, self.src_welcome_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].html_body, self.src_welcome_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].mime_type, self.src_welcome_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].name, self.src_welcome_email_template.name)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].subject, self.src_welcome_email_template.subject)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].text_body, self.src_welcome_email_template.text_body)

        self.assertEqual(directory.password_policy.reset_email_templates[0].description, self.src_reset_email_template.description)
        self.assertEqual(directory.password_policy.reset_email_templates[0].from_email_address, self.src_reset_email_template.from_email_address)
        self.assertEqual(directory.password_policy.reset_email_templates[0].from_name, self.src_reset_email_template.from_name)
        self.assertEqual(directory.password_policy.reset_email_templates[0].html_body, self.src_reset_email_template.html_body)
        self.assertEqual(directory.password_policy.reset_email_templates[0].mime_type, self.src_reset_email_template.mime_type)
        self.assertEqual(directory.password_policy.reset_email_templates[0].name, self.src_reset_email_template.name)
        self.assertEqual(directory.password_policy.reset_email_templates[0].subject, self.src_reset_email_template.subject)
        self.assertEqual(directory.password_policy.reset_email_templates[0].text_body, self.src_reset_email_template.text_body)

        self.assertEqual(directory.password_policy.reset_success_email_templates[0].description, self.src_reset_success_email_template.description)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].from_email_address, self.src_reset_success_email_template.from_email_address)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].from_name, self.src_reset_success_email_template.from_name)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].html_body, self.src_reset_success_email_template.html_body)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].mime_type, self.src_reset_success_email_template.mime_type)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].name, self.src_reset_success_email_template.name)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].subject, self.src_reset_success_email_template.subject)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].text_body, self.src_reset_success_email_template.text_body)

    def test_migrate(self):
        migrator = DirectoryWorkflowMigrator(destination_directory=self.dst_dir, source_directory=self.src_dir)
        directory = migrator.migrate()

        self.assertEqual(directory.account_creation_policy.verification_email_status, self.src_dir.account_creation_policy.verification_email_status)
        self.assertEqual(directory.account_creation_policy.verification_success_email_status, self.src_dir.account_creation_policy.verification_success_email_status)
        self.assertEqual(directory.account_creation_policy.welcome_email_status, self.src_dir.account_creation_policy.welcome_email_status)

        self.assertEqual(directory.password_policy.reset_email_status, self.src_dir.password_policy.reset_email_status)
        self.assertEqual(directory.password_policy.reset_success_email_status, self.src_dir.password_policy.reset_success_email_status)
        self.assertEqual(directory.password_policy.reset_token_ttl, self.src_dir.password_policy.reset_token_ttl)

        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].description, self.src_verification_email_template.description)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].from_email_address, self.src_verification_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].from_name, self.src_verification_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].html_body, self.src_verification_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].mime_type, self.src_verification_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].name, self.src_verification_email_template.name)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].subject, self.src_verification_email_template.subject)
        self.assertEqual(directory.account_creation_policy.verification_email_templates[0].text_body, self.src_verification_email_template.text_body)

        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].description, self.src_verification_success_email_template.description)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].from_email_address, self.src_verification_success_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].from_name, self.src_verification_success_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].html_body, self.src_verification_success_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].mime_type, self.src_verification_success_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].name, self.src_verification_success_email_template.name)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].subject, self.src_verification_success_email_template.subject)
        self.assertEqual(directory.account_creation_policy.verification_success_email_templates[0].text_body, self.src_verification_success_email_template.text_body)

        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].description, self.src_welcome_email_template.description)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].from_email_address, self.src_welcome_email_template.from_email_address)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].from_name, self.src_welcome_email_template.from_name)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].html_body, self.src_welcome_email_template.html_body)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].mime_type, self.src_welcome_email_template.mime_type)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].name, self.src_welcome_email_template.name)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].subject, self.src_welcome_email_template.subject)
        self.assertEqual(directory.account_creation_policy.welcome_email_templates[0].text_body, self.src_welcome_email_template.text_body)

        self.assertEqual(directory.password_policy.reset_email_templates[0].description, self.src_reset_email_template.description)
        self.assertEqual(directory.password_policy.reset_email_templates[0].from_email_address, self.src_reset_email_template.from_email_address)
        self.assertEqual(directory.password_policy.reset_email_templates[0].from_name, self.src_reset_email_template.from_name)
        self.assertEqual(directory.password_policy.reset_email_templates[0].html_body, self.src_reset_email_template.html_body)
        self.assertEqual(directory.password_policy.reset_email_templates[0].mime_type, self.src_reset_email_template.mime_type)
        self.assertEqual(directory.password_policy.reset_email_templates[0].name, self.src_reset_email_template.name)
        self.assertEqual(directory.password_policy.reset_email_templates[0].subject, self.src_reset_email_template.subject)
        self.assertEqual(directory.password_policy.reset_email_templates[0].text_body, self.src_reset_email_template.text_body)

        self.assertEqual(directory.password_policy.reset_success_email_templates[0].description, self.src_reset_success_email_template.description)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].from_email_address, self.src_reset_success_email_template.from_email_address)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].from_name, self.src_reset_success_email_template.from_name)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].html_body, self.src_reset_success_email_template.html_body)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].mime_type, self.src_reset_success_email_template.mime_type)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].name, self.src_reset_success_email_template.name)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].subject, self.src_reset_success_email_template.subject)
        self.assertEqual(directory.password_policy.reset_success_email_templates[0].text_body, self.src_reset_success_email_template.text_body)
