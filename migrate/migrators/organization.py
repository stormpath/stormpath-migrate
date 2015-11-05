"""Our Organization Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
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
        self.destination_organization = None

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            dict(self.source_organization.custom_data)
            return self.source_organization.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Organization:', self.source_organization.href
            print err

    def copy_organization(self):
        """
        Copy the source Organization over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Organization, or None.
        """
        matches = self.destination_client.tenant.organizations.search({'name': self.source_organization.name})
        if len(matches):
            self.destination_organization = matches[0]

        try:
            data = {
                'description': self.source_organization.description,
                'name': self.source_organization.name,
                'name_key': self.source_organization.name_key,
                'status': self.source_organization.status,
            }

            if self.destination_organization:
                print 'Updating data for Organization:', self.source_organization.name
                for key, value in data.iteritems():
                    setattr(self.destination_organization, key, value)

                self.destination_organization.save()
            else:
                self.destination_organization = self.destination_client.tenant.organizations.create(data)

            return self.destination_organization
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Organization:', self.source_organization.name
            print err

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Organization.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        try:
            source_custom_data = self.source_organization.custom_data
            copied_custom_data = self.destination_organization.custom_data

            for key, value in sanitize(source_custom_data).iteritems():
                copied_custom_data[key] = value

            copied_custom_data.save()
            return copied_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Organization:', self.source_organization.href
            print err

    def migrate(self):
        """
        Migrates one Organization to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Organization, or None.
        """
        copied_org = self.copy_organization()
        self.copy_custom_data()

        print 'Successfully copied Organization:', copied_org.name
        return copied_org
