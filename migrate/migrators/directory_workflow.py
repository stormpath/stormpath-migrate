"""Our DirectoryWorkflow Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger


class DirectoryWorkflowMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath DirectoryWorkflow to another.
    """
    RESOURCE = 'directory_workflow'
    COLLECTION_RESOURCE = 'directory_workflows'

    def __init__(self, destination_directory, source_directory):
        self.destination_directory = destination_directory
        self.source_directory = source_directory

    def copy_account_creation_policy(self):
        """
        Copy the AccountCreationPolicy into the destination Directory.

        :rtype: object or None
        :returns: The updated AccountCreationPolicy object, or None.
        """
        sd = self.source_directory
        dd = self.destination_directory

        sacp = sd.account_creation_policy
        dacp = dd.account_creation_policy

        # First, we'll copy over the AccountCreationPolicy properties directly.
        # We have to do this *first* since there isn't a good way to recurse
        # into this object.
        for attr in sacp.writable_attrs:
            setattr(dacp, attr, getattr(sacp, attr))

        while True:
            try:
                dacp.save()
                break
            except StormpathError as err:
                logger.error('Failed to copy AccountCreationPolicy for Directory: {} ({})'.format(sd.name, err))

        # Once we get here, we're going to copy over all the
        # AccountCreationPolicy email templates.
        resources_to_copy = [
            'verification_email_templates',
            'verification_success_email_templates',
            'welcome_email_templates'
        ]

        for resource in resources_to_copy:
            sr = getattr(sacp, resource)[0]
            dr = getattr(dacp, resource)[0]

            for attr in sr.writable_attrs:
                setattr(dr, attr, getattr(sr, attr))

            while True:
                try:
                    dr.save()
                    break
                except StormpathError as err:
                    logger.error('Failed to copy {} for Directory: {} ({})'.format(resource, sd.name, err))

    def copy_password_policy(self):
        """
        Copy the PasswordPolicy into the destination Directory.

        :rtype: object or None
        :returns: The updated PasswordPolicy object, or None.
        """
        sd = self.source_directory
        dd = self.destination_directory

        spp = sd.password_policy
        dpp = dd.password_policy

        spsp = spp.strength
        dpsp = dpp.strength

        # First, we'll copy over the PasswordPolicy properties directly.
        # We have to do this *first* since there isn't a good way to recurse
        # into this object.
        for attr in spp.writable_attrs:
            setattr(dpp, attr, getattr(spp, attr))

        while True:
            try:
                dpp.save()
                break
            except StormpathError as err:
                logger.error('Failed to copy PasswordPolicy for Directory: {} ({})'.format(sd.name, err))

        # Next, we'll copy over the PasswordStrength properties.
        for attr in spsp.writable_attrs:
            setattr(dpsp, attr, getattr(spsp, attr))

        while True:
            try:
                dpsp.save()
                break
            except StormpathError as err:
                logger.error('Failed to copy PasswordStrength for Directory: {} ({})'.format(sd.name, err))

        # Once we get here, we're going to copy over all the
        # AccountCreationPolicy email templates.
        resources_to_copy = [
            'reset_email_templates',
            'reset_success_email_templates',
        ]

        for resource in resources_to_copy:
            sr = getattr(spp, resource)[0]
            dr = getattr(dpp, resource)[0]

            for attr in sr.writable_attrs:
                setattr(dr, attr, getattr(sr, attr))

            while True:
                try:
                    dr.save()
                    break
                except StormpathError as err:
                    logger.error('Failed to copy {} for Directory: {} ({})'.format(resource, sd.name, err))

    def migrate(self):
        """
        Migrates one DirectoryWorkflow to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Directory, or None.
        """
        self.copy_account_creation_policy()
        self.copy_password_policy()

        logger.info('Successfully copied Workflow for Directory: {}'.format(self.destination_directory.name))
        return self.destination_directory
