"""Our Group Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class GroupMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Group to another.
    """
    RESOURCE = 'groups'
    COLLECTION_RESOURCE = 'groups'

    def __init__(self, destination_directory, source_group):
        self.destination_directory = destination_directory
        self.source_group = source_group
        self.destination_group = None

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            dict(self.source_group.custom_data)
            return self.source_group.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Group:', self.source_group.href
            print err

    def copy_group(self):
        """
        Copy the source Group over into the destination Directory.

        :rtype: object (or None)
        :returns: The copied Group, or None.
        """
        matches = self.destination_directory.groups.search({'name': self.source_group.name})
        if len(matches):
            self.destination_group = matches[0]

        try:
            data = {
                'description': self.source_group.description,
                'name': self.source_group.name,
                'status': self.source_group.status,
            }

            if self.destination_group:
                print 'Updating data for Group:', self.source_group.name
                for key, value in data.iteritems():
                    setattr(self.destination_group, key, value)

                self.destination_group.save()
            else:
                self.destination_group = self.destination_directory.groups.create(data)

            return self.destination_group
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Group:', self.source_group.name
            print err

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Group.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        try:
            source_custom_data = self.source_group.custom_data
            copied_custom_data = self.destination_group.custom_data

            for key, value in sanitize(source_custom_data).iteritems():
                copied_custom_data[key] = value

            copied_custom_data.save()
            return copied_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Group:', self.source_group.href
            print err

    def migrate(self):
        """
        Migrates one Group to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Group, or None.
        """
        copied_group = self.copy_group()
        if copied_group:
            copied_custom_data = self.copy_custom_data()

        print 'Successfully copied Group:', copied_group.name
        return copied_group
