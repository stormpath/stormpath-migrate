"""Our DirectoryWorkflow Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class DirectoryWorkflowMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath DirectoryWorkflow to another.
    """
    RESOURCE = 'directory_workflow'
    COLLECTION_RESOURCE = 'directory_workflows'

    def __init__(self, destination_directory, source_directory):
        self.destination_directory = destination_directory
        self.source_directory = source_directory

    def get_verification_email_template(self):
        """
        Retrieve the VerificationEmailTemplate.

        :rtype: object (or None)
        :returns: The VerificationEmailTemplate object, or None.
        """
        try:
            self.verification_email_template = self.source_directory.account_creation_policy.verification_email_templates[0]
            return self.verification_email_template
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch VerificationEmailTemplate for Directory:', self.source_directory.href
            print err

    def get_verification_success_email_template(self):
        """
        Retrieve the VerificationSuccessEmailTemplate.

        :rtype: object (or None)
        :returns: The VerificationSuccessEmailTemplate, or None.
        """
        try:
            self.verification_success_email_template = self.source_directory.account_creation_policy.verification_success_email_templates[0]
            return self.verification_success_email_template
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch VerificationSuccessEmailTemplate for Directory:', self.source_directory.href
            print err

    def get_welcome_email_template(self):
        """
        Retrieve the WelcomeEmailTemplate.

        :rtype: object (or None)
        :returns: The WelcomeEmailTemplate, or None.
        """
        try:
            self.welcome_email_template = self.source_directory.account_creation_policy.welcome_email_templates[0]
            return self.welcome_email_template
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch WelcomeEmailTemplate for Directory:', self.source_directory.href
            print err

    def get_reset_email_template(self):
        """
        Retrieve the ResetEmailTemplate.

        :rtype: object (or None)
        :returns: The ResetEmailTemplate, or None.
        """
        try:
            self.reset_email_template = self.source_directory.password_policy.reset_email_templates[0]
            return self.reset_email_template
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch ResetEmailTemplate for Directory:', self.source_directory.href
            print err

    def get_reset_success_email_template(self):
        """
        Retrieve the ResetSuccessEmailTemplate.

        :rtype: object (or None)
        :returns: The ResetSuccessEmailTemplate, or None.
        """
        try:
            self.reset_success_email_template = self.source_directory.password_policy.reset_success_email_templates[0]
            return self.reset_success_email_template
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch ResetSuccessEmailTemplate for Directory:', self.source_directory.href
            print err

    def copy_workflow(self):
        """
        Copy the source Workflows over into the destination Tenant.

        :rtype: object or None
        :returns: The updated Directory object, or None.
        """
        try:
            self.get_verification_email_template()
            self.get_verification_success_email_template()
            self.get_welcome_email_template()
            self.get_reset_email_template()
            self.get_reset_success_email_template()

            source_account_creation_policy = self.source_directory.account_creation_policy
            destination_account_creation_policy = self.destination_directory.account_creation_policy

            destination_account_creation_policy.verification_email_status = source_account_creation_policy.verification_email_status
            destination_account_creation_policy.verification_success_email_status = source_account_creation_policy.verification_success_email_status
            destination_account_creation_policy.welcome_email_status = source_account_creation_policy.welcome_email_status
            destination_account_creation_policy.save()

            source_password_policy = self.source_directory.password_policy
            destination_password_policy = self.destination_directory.password_policy

            destination_password_policy.reset_email_status = source_password_policy.reset_email_status
            destination_password_policy.reset_success_email_status = source_password_policy.reset_success_email_status
            destination_password_policy.reset_token_ttl = source_password_policy.reset_token_ttl
            destination_password_policy.save()

            self.destination_verification_email_template = self.destination_directory.account_creation_policy.verification_email_templates[0]
            self.destination_verification_success_email_template = self.destination_directory.account_creation_policy.verification_success_email_templates[0]
            self.destination_welcome_email_template = self.destination_directory.account_creation_policy.welcome_email_templates[0]
            self.destination_reset_email_template = self.destination_directory.password_policy.reset_email_templates[0]
            self.destination_reset_success_email_template = self.destination_directory.password_policy.reset_success_email_templates[0]

            self.destination_verification_email_template.description = self.verification_email_template.description
            self.destination_verification_email_template.from_email_address = self.verification_email_template.from_email_address
            self.destination_verification_email_template.from_name = self.verification_email_template.from_name
            self.destination_verification_email_template.html_body = self.verification_email_template.html_body
            self.destination_verification_email_template.mime_type = self.verification_email_template.mime_type
            self.destination_verification_email_template.name = self.verification_email_template.name
            self.destination_verification_email_template.subject = self.verification_email_template.subject
            self.destination_verification_email_template.text_body = self.verification_email_template.text_body
            self.destination_verification_email_template.save()

            self.destination_verification_success_email_template.description = self.verification_success_email_template.description
            self.destination_verification_success_email_template.from_email_address = self.verification_success_email_template.from_email_address
            self.destination_verification_success_email_template.from_name = self.verification_success_email_template.from_name
            self.destination_verification_success_email_template.html_body = self.verification_success_email_template.html_body
            self.destination_verification_success_email_template.mime_type = self.verification_success_email_template.mime_type
            self.destination_verification_success_email_template.name = self.verification_success_email_template.name
            self.destination_verification_success_email_template.subject = self.verification_success_email_template.subject
            self.destination_verification_success_email_template.text_body = self.verification_success_email_template.text_body
            self.destination_verification_success_email_template.save()

            self.destination_welcome_email_template.description = self.welcome_email_template.description
            self.destination_welcome_email_template.from_email_address = self.welcome_email_template.from_email_address
            self.destination_welcome_email_template.from_name = self.welcome_email_template.from_name
            self.destination_welcome_email_template.html_body = self.welcome_email_template.html_body
            self.destination_welcome_email_template.mime_type = self.welcome_email_template.mime_type
            self.destination_welcome_email_template.name = self.welcome_email_template.name
            self.destination_welcome_email_template.subject = self.welcome_email_template.subject
            self.destination_welcome_email_template.text_body = self.welcome_email_template.text_body
            self.destination_welcome_email_template.save()

            self.destination_reset_email_template.description = self.reset_email_template.description
            self.destination_reset_email_template.from_email_address = self.reset_email_template.from_email_address
            self.destination_reset_email_template.from_name = self.reset_email_template.from_name
            self.destination_reset_email_template.html_body = self.reset_email_template.html_body
            self.destination_reset_email_template.mime_type = self.reset_email_template.mime_type
            self.destination_reset_email_template.name = self.reset_email_template.name
            self.destination_reset_email_template.subject = self.reset_email_template.subject
            self.destination_reset_email_template.text_body = self.reset_email_template.text_body
            self.destination_reset_email_template.save()

            self.destination_reset_success_email_template.description = self.reset_success_email_template.description
            self.destination_reset_success_email_template.from_email_address = self.reset_success_email_template.from_email_address
            self.destination_reset_success_email_template.from_name = self.reset_success_email_template.from_name
            self.destination_reset_success_email_template.html_body = self.reset_success_email_template.html_body
            self.destination_reset_success_email_template.mime_type = self.reset_success_email_template.mime_type
            self.destination_reset_success_email_template.name = self.reset_success_email_template.name
            self.destination_reset_success_email_template.subject = self.reset_success_email_template.subject
            self.destination_reset_success_email_template.text_body = self.reset_success_email_template.text_body
            self.destination_reset_success_email_template.save()

            return self.destination_directory
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Workflow:', self.source_directory.href
            print err

    def migrate(self):
        """
        Migrates one DirectoryWorkflow to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Directory, or None.
        """
        copied_workflow = None

        while not copied_workflow:
            copied_workflow = self.copy_workflow()

        print 'Successfully copied Workflow:', copied_workflow.href
        return copied_workflow
