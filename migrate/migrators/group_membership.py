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

    def __init__(self, destination_client, source_group_membership):
        self.destination_client = destination_client
        self.source_group_membership = source_group_membership

    def get_destination_directory(self):
        """
        Retrieve the destination Directory.

        :rtype: object (or None)
        :returns: The Directory, or None.
        """
        dc = self.destination_client
        sgm = self.source_group_membership
        sd = sgm.group.directory

        while True:
            try:
                matches = dc.directories.search({'name': sd.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Directory: {} ({})'.format(sd.name, err))

    def get_destination_group(self):
        """
        Retrieve the destination Group.

        :rtype: object (or None)
        :returns: The Group, or None.
        """
        dd = self.destination_directory
        sg = self.source_group_membership.group

        while True:
            try:
                matches = dd.groups.search({'name': sg.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Group: {} in Directory: {} ({})'.format(sg.name, dd.name, err))

    def get_destination_account(self):
        """
        Retrieve the destination Account.

        :rtype: object (or None)
        :returns: The Account, or None.
        """
        dd = self.destination_directory
        sa = self.source_group_membership.account

        while True:
            try:
                matches = dd.accounts.search({'username': sa.username})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Account: {} in Directory: {} ({})'.format(sa.username, dd.name, err))

    def copy_membership(self):
        """
        Copy the source Membership over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Group, or None.
        """
        da = self.destination_account
        dc = self.destination_client
        dg = self.destination_group
        dd = self.destination_directory

        for membership in da.group_memberships:
            if membership.group.href == dg.href:
                return membership

        while True:
            try:
                return dc.group_memberships.create({'account': da, 'group': dg})
            except StormpathError as err:
                logger.error('Failed to copy GroupMembership for Account: {} and Group: {} in Directory: {} ({})'.format(da.username, dg.name, dd.name, err))

    def migrate(self):
        """
        Migrates one Membership to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Membership, or None.
        """
        sa = self.source_group_membership.account
        sd = self.source_group_membership.account.directory
        sg = self.source_group_membership.group

        self.destination_directory = self.get_destination_directory()
        self.destination_group = self.get_destination_group()
        self.destination_account = self.get_destination_account()

        # If the destination resources can't be found, we need to exit the
        # process ASAP.  This means something horrible is happening -- maybe a
        # client is concurrently deleting resources on the SOURCE or DESTINATION
        # and messing things up.
        if not self.destination_directory:
            logger.critical('The Directory: {} does not exist in the destination. This is a fatal error.'.format(sg.directory.name))
            raise RuntimeError('Read the log.')
        elif not self.destination_group:
            logger.warning('The Group: {} does not exist in the destination Directory: {}.  Skipping Membership migration.'.format(sg.name, sd.name))
        elif not self.destination_account:
            logger.warning('The Account: {} does not exist in the destination Directory: {}.  Skipping Membership migration.'.format(sa.username, sd.name))
        else:
            membership = self.copy_membership()
            logger.info('Successfully copied GroupMembership for Account: {} and Group: {} in Directory: {}'.format(sa.username, sg.name, sd.name))

            return membership
