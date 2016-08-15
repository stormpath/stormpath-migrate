"""Our Group Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
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

    def get_destination_group(self):
        """
        Retrieve the destination Group.

        :rtype: object (or None)
        :returns: The Group object, or None.
        """
        sg = self.source_group
        dd = self.destination_directory

        while True:
            try:
                matches = dd.groups.search({'name': sg.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Group: {} in Directory: {} ({})'.format(sg.name.encode('utf-8'), dd.name.encode('utf-8'), err))

    def copy_group(self):
        """
        Copy the source Group over into the destination Directory.

        :rtype: object (or None)
        :returns: The copied Group, or None.
        """
        dd = self.destination_directory
        sg = self.source_group
        dg = self.destination_group

        data = {
            'description': sg.description,
            'name': sg.name,
            'status': sg.status,
        }

        # If this Group already exists, we'll just update it.
        if dg:
            for key, value in data.items():
                setattr(dg, key, value)

            while True:
                try:
                    dg.save()
                    return dg
                except StormpathError as err:
                    logger.error('Failed to copy Group: {} into Directory: {} ({})'.format(sg.name.encode('utf-8'), dd.name.encode('utf-8'), err))

        # If we get here, it means we need to create the Group from scratch.
        while True:
            try:
                return dd.groups.create(data)
            except StormpathError as err:
                logger.error('Failed to copy Group: {} into Directory: {} ({})'.format(sg.name.encode('utf-8'), dd.name.encode('utf-8'), err))

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Group.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        sg = self.source_group
        dg = self.destination_group
        dd = self.destination_directory

        for key, value in sanitize(sg.custom_data).items():
            dg.custom_data[key] = value

        try:
            dg.custom_data.save()
            return dg.custom_data
        except StormpathError, err:
            logger.error('Failed to copy CustomData for Group: {} in Directory: {} ({})'.format(sg.name.encode('utf-8'), dd.name.encode('utf-8'), err))

    def migrate(self):
        """
        Migrates one Group to another Tenant =)  Won't stop until the
        migration is complete.

        :rtype: object (or None)
        :returns: The migrated Group, or None.
        """
        self.destination_group = self.get_destination_group()
        self.destination_group = self.copy_group()
        self.copy_custom_data()

        logger.info('Successfully copied Group: {}'.format(self.destination_group.name.encode('utf-8')))
        return self.destination_group
