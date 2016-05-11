"""Our GroupMembership Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger


class GroupMembershipMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath ApplicationAccountStoreMapping to another.
    """
    RESOURCE = 'group_membership'
    COLLECTION_RESOURCE = 'group_memberships'

    def __init__(self, destination_client, destination_account, source_group):
        self.destination_client = destination_client
        self.destination_account = destination_account
        self.source_group = source_group
        self.destination_directory = None
        self.destination_group = None

    def get_destination_directory(self):
        """
        Retrieve the destination Directory.

        :rtype: object (or None)
        :returns: The Directory, or None.
        """
        source_directory = self.source_group.directory

        try:
            matches = self.destination_client.directories.search({'name': source_directory.name})
        except StormpathError as err:
            logger.error('Could not fetch destination Directory: {}: {}'.format(source_directory.name, err))
            return

        if len(matches):
            self.destination_directory = matches[0]
            return self.destination_directory

        logger.error('Could not find destination Directory: {}'.format(source_directory.name))

    def get_destination_group(self):
        """
        Retrieve the destination Group.

        :rtype: object (or None)
        :returns: The Group, or None.
        """
        try:
            matches = self.destination_directory.groups.search({'name': self.source_group.name})
        except StormpathError as err:
            logger.error('Could not fetch destination Group: {}: {}'.format(self.source_group.name, err))
            return

        if len(matches):
            self.destination_group = matches[0]
            return self.destination_group

        logger.error('Could not find destination Group: {}'.format(self.source_group.name))

    def copy_membership(self):
        """
        Copy the source Membership over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Group, or None.
        """
        if not (self.get_destination_directory() and self.get_destination_group()):
            return

        for group in self.destination_account.groups:
            if group.href == self.destination_group.href:
                return self.destination_group

        try:
            self.destination_group_membership = self.destination_client.group_memberships.create({
                'account': self.destination_account,
                'group': self.destination_group,
            })

            return self.destination_group_membership
        except StormpathError, err:
            logger.error('Could not create destination Membership: {}'.format(err))

    def migrate(self):
        """
        Migrates one Membership to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Membership, or None.
        """
        copied_membership = self.copy_membership()

        if copied_membership:
            logger.info('Successfully copied GroupMembership for Account: {} and Group: {}'.format(
                self.destination_account.email,
                self.source_group.name
            ))
            return copied_membership
        else:
            logger.error('Failed to copy GroupMembership for Account: {} and Group: {}'.format(
                self.destination_account.email,
                self.source_group.name
            ))
