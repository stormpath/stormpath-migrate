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
        self.destination_group_membership = None

    def get_destination_account(self):
        """
        Retrieve the destination Account.

        :rtype: object (or None)
        :returns: The Account, or None.
        """
        try:
            source_account = self.source_group_membership.account
            source_directory = source_account.directory

            destination_directory = self.destination_client.directories.search({'name': source_directory.name})[0]
            self.destination_account = destination_directory.accounts.search({'email': source_account.email})[0]

            return self.destination_account
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch Account for Membership:', self.source_group_membership.href
            print err

    def get_destination_group(self):
        """
        Retrieve the destination Group.

        :rtype: object (or None)
        :returns: The Group, or None.
        """
        try:
            source_group = self.source_group_membership.group
            source_directory = source_group.directory

            destination_directory = self.destination_client.directories.search({'name': source_directory.name})[0]
            self.destination_group = destination_directory.groups.search({'name': source_group.name})[0]

            return self.destination_group
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch Group for Membership:', self.source_group_membership.href
            print err

    def copy_membership(self):
        """
        Copy the source Membership over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Membership, or None.
        """
        try:
            self.get_destination_account()
            self.get_destination_group()

            self.destination_group_membership = self.destination_client.group_memberships.create({
                'account': self.destination_account,
                'group': self.destination_group,
            })
            return self.destination_group_membership
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Membership:', self.source_group_membership.href
            print err

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

        print 'Successfully copied Membership:', copied_membership.href
        return copied_membership
