"""Our GroupMembership Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator


class GroupMembershipMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath ApplicationAccountStoreMapping to another.
    """
    RESOURCE = 'group_membership'
    COLLECTION_RESOURCE = 'group_memberships'

    def __init__(self, destination_client, source_group_membership):
        self.destination_client = destination_client
        self.source_group_membership = source_group_membership
        self.destination_account = None
        self.destination_group = None
        self.destination_group_membership = None

    def get_destination_account(self):
        """
        Retrieve the destination Account.

        :rtype: object (or None)
        :returns: The Account, or None.
        """
        source_account = self.source_group_membership.account
        source_directory = source_account.directory

        try:
            matches = self.destination_client.directories.search({'name': source_directory.name})
        except StormpathError as err:
            self.log.error('Could not fetch destination Directory: {}: {}'.format(source_directory.name, err))
            return

        if len(matches) == 0:
            self.log.error('[GROUP MEMBERSHIP]: Could not find destination Directory: {}'.format(source_directory.name))
            return

        destination_directory = matches[0]

        try:
            matches = destination_directory.accounts.search({'email': source_account.email})
        except StormpathError as err:
            self.log.error('[GROUP MEMBERSHIP]: Could not fetch destination Account: {}: {}'.format(source_account.email, err))
            return

        if len(matches) == 0:
            self.log.error('[GROUP MEMBERSHIP]: Could not find destination Account: {}'.format(source_account.email))
            return

        self.destination_account = matches[0]
        return self.destination_account

    def get_destination_group(self):
        """
        Retrieve the destination Group.

        :rtype: object (or None)
        :returns: The Group, or None.
        """
        source_group = self.source_group_membership.group
        source_directory = source_group.directory

        try:
            matches = self.destination_client.directories.search({'name': source_directory.name})
        except StormpathError as err:
            self.log.error('[GROUP MEMBERSHIP]: Could not fetch destination Directory: {}: {}'.format(source_directory.name, err))
            return

        if len(matches) == 0:
            self.log.error('[GROUP MEMBERSHIP]: Could not find destination Directory: {}'.format(source_directory.name))
            return

        destination_directory = matches[0]

        try:
            matches = destination_directory.groups.search({'name': source_group.name})
        except StormpathError as err:
            self.log.error('[GROUP MEMBERSHIP]: Could not fetch destination Group: {}: {}'.format(source_group.name, err))
            return

        if len(matches) == 0:
            self.log.error('[GROUP MEMBERSHIP]: Could not find destination Group: {}'.format(source_group.name))
            return

        self.destination_group = matches[0]
        return self.destination_group

    def copy_membership(self):
        """
        Copy the source Membership over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Membership, or None.
        """
        if not (self.get_destination_account() and self.get_destination_group()):
            return

        for membership in self.destination_account.group_memberships:
            if membership.account.href == self.destination_account.href and membership.group.href == self.destination_group.href:
                return membership

        try:
            self.destination_group_membership = self.destination_client.group_memberships.create({
                'account': self.destination_account,
                'group': self.destination_group,
            })

            return self.destination_group_membership
        except StormpathError, err:
            self.log.error('[GROUP MEMBERSHIP]: Could not create destination Membership: {}'.format(err))
            return

    def migrate(self):
        """
        Migrates one Membership to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Membership, or None.
        """
        copied_membership = None

        while not copied_membership:
            copied_membership = self.copy_membership()

        self.log.info('[GROUP MEMBERSHIP]: Successfully copied GroupMembership for Account: {}'.format(self.source_group_membership.account.email))
        return copied_membership
