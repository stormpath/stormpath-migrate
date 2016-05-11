"""Our ApplicationAccountStoreMapping Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator


class ApplicationAccountStoreMappingMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath ApplicationAccountStoreMapping to another.
    """
    RESOURCE = 'account_store_mapping'
    COLLECTION_RESOURCE = 'account_store_mappings'

    def __init__(self, destination_application, source_account_store_mapping):
        self.destination_application = destination_application
        self.source_account_store_mapping = source_account_store_mapping
        self.destination_account_store_mapping = None

    def get_source_account_store(self):
        """
        Retrieve the source AccountStore (either Directory, Organization,
        or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        try:
            self.source_account_store = self.source_account_store_mapping.account_store
            return self.source_account_store
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch AccountStore for Mapping:', self.source_account_store_mapping.href
            print err

    def get_destination_account_store(self):
        """
        Retrieve the destination AccountStore (either Directory, Organization,
        or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        try:
            tenant = self.destination_application.tenant
            klass = self.source_account_store.__class__.__name__

            if klass == 'Directory':
                self.destination_account_store = tenant.directories.search({'name': self.source_account_store.name})[0]
            elif klass == 'Organization':
                self.destination_account_store = tenant.organizations.search({'name': self.source_account_store.name})[0]
            elif klass == 'Group':
                self.destination_account_store = tenant.groups.search({'name': self.source_account_store.name})[0]

            return self.destination_account_store
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch AccountStore for Mapping:', self.source_account_store_mapping.href
            print err

    def copy_mapping(self):
        """
        Copy the source Mapping over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Mapping, or None.
        """
        try:
            self.get_source_account_store()
            destination_account_store = self.get_destination_account_store()

            for mapping in self.destination_application.account_store_mappings:
                if mapping.account_store.href == destination_account_store.href and mapping.application.href == self.destination_application.href:
                    return mapping

            self.destination_account_store_mapping = self.destination_application.account_store_mappings.create({
                'account_store': destination_account_store,
                'application': self.destination_application,
                'list_index': self.source_account_store_mapping.list_index,
                'is_default_account_store': self.source_account_store_mapping.is_default_account_store,
                'is_default_group_store': self.source_account_store_mapping.is_default_group_store,
            })
            return self.destination_account_store_mapping
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Mapping:', self.source_account_store_mapping.href
            print err

    def migrate(self):
        """
        Migrates one Mapping to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Mapping, or None.
        """
        copied_mapping = None

        while not copied_mapping:
            copied_mapping = self.copy_mapping()

        print 'Successfully copied Mapping:', copied_mapping.href
        return copied_mapping


class OrganizationAccountStoreMappingMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath OrganizationAccountStoreMapping to another.
    """
    RESOURCE = 'account_store_mapping'
    COLLECTION_RESOURCE = 'account_store_mappings'

    def __init__(self, destination_organization, source_account_store_mapping):
        self.destination_organization = destination_organization
        self.source_account_store_mapping = source_account_store_mapping
        self.destination_account_store_mapping = None

    def get_source_account_store(self):
        """
        Retrieve the source AccountStore (either Directory or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        try:
            self.source_account_store = self.source_account_store_mapping.account_store
            return self.source_account_store
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch AccountStore for Mapping:', self.source_account_store_mapping.href
            print err

    def get_destination_account_store(self):
        """
        Retrieve the destination AccountStore (either Directory or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        try:
            tenant = self.destination_organization.tenant
            klass = self.source_account_store.__class__.__name__

            if klass == 'Directory':
                self.destination_account_store = tenant.directories.search({'name': self.source_account_store.name})[0]
            elif klass == 'Group':
                self.destination_account_store = tenant.groups.search({'name': self.source_account_store.name})[0]

            return self.destination_account_store
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch AccountStore for Mapping:', self.source_account_store_mapping.href
            print err

    def copy_mapping(self):
        """
        Copy the source Mapping over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Mapping, or None.
        """
        try:
            self.get_source_account_store()
            destination_account_store = self.get_destination_account_store()

            for mapping in self.destination_organization.account_store_mappings:
                if mapping.account_store.href == destination_account_store.href and mapping.organization.href == self.destination_organization.href:
                    return mapping

            self.destination_account_store_mapping = self.destination_organization._client.organization_account_store_mappings.create({
                'account_store': destination_account_store,
                'organization': self.destination_organization,
                'list_index': self.source_account_store_mapping.list_index,
                'is_default_account_store': self.source_account_store_mapping.is_default_account_store,
                'is_default_group_store': self.source_account_store_mapping.is_default_group_store,
            })
            return self.destination_account_store_mapping
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Mapping:', self.source_account_store_mapping.href
            print err

    def migrate(self):
        """
        Migrates one Mapping to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Mapping, or None.
        """
        copied_mapping = self.copy_mapping()

        print 'Successfully copied Mapping:', copied_mapping.href
        return copied_mapping
