"""Our Organization Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
from ..utils import sanitize


class OrganizationMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Organization to another.
    """
    RESOURCE = 'organization'
    COLLECTION_RESOURCE = 'organizations'

    def __init__(self, destination_client, source_organization):
        self.destination_client = destination_client
        self.source_organization = source_organization

    def get_destination_org(self):
        """
        Retrieve the destination Organization.

        :rtype: object (or None)
        :returns: The Organization object, or None.
        """
        dc = self.destination_client
        so = self.source_organization

        while True:
            try:
                matches = dc.organizations.search({'name': so.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Organization: {} ({})'.format(so.name, err))

    def copy_org(self):
        """
        Copy the source Organization over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Organization, or None.
        """
        so = self.source_organization
        dc = self.destination_client
        do = self.destination_organization

        data = {
            'description': so.description,
            'name': so.name,
            'name_key': so.name_key,
            'status': so.status,
        }

        # If this Organization already exists, we'll just update it.
        if do:
            for key, value in data.items():
                setattr(do, key, value)

            while True:
                try:
                    do.save()
                    return do
                except StormpathError as err:
                    logger.error('Failed to copy Organization: {} ({})'.format(so.name, err))

        # If we get here, it means we need to create the Organization from
        # scratch.
        while True:
            try:
                return dc.tenant.organizations.create(data)
            except StormpathError as err:
                logger.error('Failed to copy Organization: {} ({})'.format(so.name, err))

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Organization.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        so = self.source_organization
        do = self.destination_organization

        for key, value in sanitize(so.custom_data).items():
            do.custom_data[key] = value

        while True:
            try:
                do.custom_data.save()
                return do.custom_data
            except StormpathError as err:
                logger.error('Failed to copy CustomData for Organization: {} ({})'.format(so.name, err))

    def migrate(self):
        """
        Migrates one Organization to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Organization, or None.
        """
        self.destination_organization = self.get_destination_org()
        self.destination_organization = self.copy_org()
        self.copy_custom_data()

        logger.info('Successfully copied Organization: {}'.format(self.destination_organization.name))
        return self.destination_organization
