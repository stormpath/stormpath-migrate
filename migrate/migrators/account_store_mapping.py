"""Our ApplicationAccountStoreMapping Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger


class ApplicationAccountStoreMappingMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath ApplicationAccountStoreMapping to another.
    """
    RESOURCE = 'account_store_mapping'
    COLLECTION_RESOURCE = 'account_store_mappings'

    def __init__(self, destination_application, source_account_store_mapping):
        self.destination_application = destination_application
        self.source_account_store_mapping = source_account_store_mapping

    def get_destination_account_store(self):
        """
        Retrieve the destination AccountStore (either Directory, Organization,
        or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        tenant = self.destination_tenant
        sas = self.source_account_store

        klass = sas.__class__.__name__
        collection = 'directories' if klass == 'Directory' else klass.lower() + 's'

        while True:
            try:
                matches = getattr(tenant, collection).search({'name': sas.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to fetch destination {}: {} ({})'.format(klass, sas.name.encode('utf-8'), err))

    def copy_mapping(self):
        """
        Copy the source Mapping over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Mapping, or None.
        """
        da = self.destination_application
        das = self.destination_account_store
        sasm = self.source_account_store_mapping

        # First, we'll check to see if this mapping already exists.  If it does,
        # we'll return immediately as there's nothing to do here.
        for mapping in da.account_store_mappings:
            if mapping.account_store.href == das.href and mapping.application.href == da.href:
                return mapping

        while True:
            try:
                return da.account_store_mappings.create({
                    'account_store': das,
                    'application': da,
                    'list_index': sasm.list_index,
                    'is_default_account_store': sasm.is_default_account_store,
                    'is_default_group_store': sasm.is_default_group_store,
                })
            except StormpathError as err:
                logger.error('Failed to copy AccountStoreMapping from Application: {} to {} {} ({})'.format(
                    da.name.encode('utf-8'),
                    das.__class__.__name__,
                    das.name.encode('utf-8'),
                    err
                ))

    def migrate(self):
        """
        Migrates one Mapping to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Mapping, or None.
        """
        self.destination_tenant = self.destination_application.tenant
        self.source_account_store = self.source_account_store_mapping.account_store
        self.destination_account_store = self.get_destination_account_store()

        if not self.destination_account_store:
            logger.warning('Skipping creation of AccountStoreMapping from Application: {} to {} {} (The destination AccountStore does not exist)'.format(
                self.destination_application.name.encode('utf-8'),
                self.source_account_store.__class__.__name__,
                self.source_account_store.name.encode('utf-8')
            ))
            return

        mapping = self.copy_mapping()
        logger.info('Successfully copied source AccountStoreMapping from Application: {} to {} {}.'.format(
            self.destination_application.name.encode('utf-8'),
            self.destination_account_store.__class__.__name__,
            self.destination_account_store.name.encode('utf-8')
        ))

        return mapping


class OrganizationAccountStoreMappingMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath OrganizationAccountStoreMapping to another.
    """
    RESOURCE = 'account_store_mapping'
    COLLECTION_RESOURCE = 'account_store_mappings'

    def __init__(self, destination_organization, source_account_store_mapping):
        self.destination_organization = destination_organization
        self.source_account_store_mapping = source_account_store_mapping

    def get_destination_account_store(self):
        """
        Retrieve the destination AccountStore (either Directory or Group).

        :rtype: object (or None)
        :returns: The AccountStore, or None.
        """
        tenant = self.destination_tenant
        sas = self.source_account_store

        klass = sas.__class__.__name__
        collection = 'directories' if klass == 'Directory' else klass.lower() + 's'

        while True:
            try:
                matches = getattr(tenant, collection).search({'name': sas.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to fetch destination {}: {} ({})'.format(klass, sas.name.encode('utf-8'), err))

    def copy_mapping(self):
        """
        Copy the source Mapping over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Mapping, or None.
        """
        do = self.destination_organization
        das = self.destination_account_store
        sasm = self.source_account_store_mapping

        # First, we'll check to see if this mapping already exists.  If it does,
        # we'll return immediately as there's nothing to do here.
        for mapping in do.account_store_mappings:
            if mapping.account_store.href == das.href and mapping.organization.href == do.href:
                return mapping

        while True:
            try:
                return do.account_store_mappings._client.organization_account_store_mappings.create({
                    'account_store': das,
                    'organization': do,
                    'list_index': sasm.list_index,
                    'is_default_account_store': sasm.is_default_account_store,
                    'is_default_group_store': sasm.is_default_group_store,
                })
            except StormpathError as err:
                logger.error('Failed to copy AccountStoreMapping from Organization: {} to {} {} ({})'.format(
                    do.name.encode('utf-8'),
                    das.__class__.__name__,
                    das.name.encode('utf-8'),
                    err
                ))

    def migrate(self):
        """
        Migrates one Mapping to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Mapping, or None.
        """
        self.destination_tenant = self.destination_organization.tenant
        self.source_account_store = self.source_account_store_mapping.account_store
        self.destination_account_store = self.get_destination_account_store()

        if not self.destination_account_store:
            logger.warning('Skipping creation of AccountStoreMapping from Organization: {} to {} {} (The destination AccountStore does not exist)'.format(
                self.destination_organization.name.encode('utf-8'),
                self.source_account_store.__class__.__name__,
                self.source_account_store.name.encode('utf-8')
            ))
            return

        mapping = self.copy_mapping()
        logger.info('Successfully copied source AccountStoreMapping from Organization: {} to {} {}.'.format(
            self.destination_organization.name.encode('utf-8'),
            self.destination_account_store.__class__.__name__,
            self.destination_account_store.name.encode('utf-8')
        ))

        return mapping
