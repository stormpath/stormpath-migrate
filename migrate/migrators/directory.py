"""Our Directory Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class DirectoryMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Directory to another.
    """
    RESOURCE = 'directory'
    COLLECTION_RESOURCE = 'directories'

    def __init__(self, destination_client, source_directory):
        self.destination_client = destination_client
        self.source_directory = source_directory
        self.destination_directory = None

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            dict(self.source_directory.custom_data)
            return self.source_directory.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Directory:', self.source_directory.href
            print err

    def get_strength(self):
        """
        Retrieve the Strength.

        :rtype: object (or None)
        :returns: The Strength, or None.
        """
        try:
            strength = self.source_directory.password_policy.strength
            dict(strength)
            return strength
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch Strength for Directory:', self.source_directory.href
            print err

    def copy_dir(self):
        """
        Copy the source Directory over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Directory, or None.
        """
        try:
            data = {
                'description': self.source_directory.description,
                'name': self.source_directory.name,
                'status': self.source_directory.status,
            }

            if dict(self.source_directory.provider).get('provider_id') != 'stormpath':
                data['provider'] = sanitize(self.source_directory.provider)

            self.destination_directory = self.destination_client.directories.create(data)
            return self.destination_directory
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Directory:', self.source_directory.href
            print err

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Directory.

        :rtype: object (or None)
        :returns: The copied Strength, or None.
        """
        try:
            source_custom_data = self.source_directory.custom_data
            copied_custom_data = self.destination_directory.custom_data

            for key, value in sanitize(source_custom_data).iteritems():
                copied_custom_data[key] = value

            copied_custom_data.save()
            return copied_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Directory:', self.source_directory.href
            print err

    def copy_strength(self):
        """
        Copy the Strength rules to the given Directory.

        :rtype: object (or None)
        :returns: The copied Strength, or None.
        """
        try:
            source_strength = self.source_directory.password_policy.strength
            copied_strength = self.destination_directory.password_policy.strength

            for field in copied_strength.writable_attrs:
                copied_strength[field] = source_strength[field]

            copied_strength.save()

            return copied_strength
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Strength rules Directory:', self.source_directory.href
            print err

    def migrate(self):
        """
        Migrates one Directory to another Tenant =)  Won't stop until the
        migration is complete.

        This will copy over the Directory and Directory meta data only -- it
        will not include any Workflow settings.  This is done because Workflows
        need to be migrated separately after Accounts have been migrated -- this
        way we avoid emailing users unnecessarily when a Directory has Workflows
        enabled.

        :rtype: object (or None)
        :returns: The migrated Directory, or None.
        """
        copied_dir = None
        copied_custom_data = None
        copied_strength = None

        while not copied_dir:
            copied_dir = self.copy_dir()

        while not copied_custom_data:
            copied_custom_data = self.copy_custom_data()

        while not copied_strength:
            copied_strength = self.copy_strength()

        print 'Successfully copied Directory:', copied_dir.name
        return copied_dir
