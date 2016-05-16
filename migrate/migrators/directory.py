"""Our Directory Migrator."""


from uuid import uuid4

from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
from ..constants import MIRROR_PROVIDER_IDS, SAML_PROVIDER_ID, STORMPATH_PROVIDER_ID
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
        self.provider_id = dict(self.source_directory.provider).get('provider_id')

    def get_destination_dir(self):
        """
        Retrieve the destination Directory.

        :rtype: object (or None)
        :returns: The Directory object, or None.
        """
        sd = self.source_directory

        while True:
            try:
                matches = self.destination_client.directories.search({'name': sd.name.encode('utf-8')})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for destination Directory: {} ({})'.format(sd.name, err))

    def copy_dir(self):
        """
        Copy the source Directory over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Directory, or None.
        """
        sd = self.source_directory
        dd = self.destination_directory

        data = {
            'description': sd.description,
            'name': sd.name.encode('utf-8'),
            'status': sd.status,
        }

        # Let's dynamically generate all provider information, if necessary.  We
        # have to be careful doing this because if we supply this data for a
        # Stormpath 'cloud' Directory, shit will break.
        if self.provider_id != STORMPATH_PROVIDER_ID:
            data['provider'] = sanitize(sd.provider)

        if self.provider_id in MIRROR_PROVIDER_IDS:
            data['provider']['agent'] = sanitize(sd.provider.agent)
            data['provider']['agent']['config'] = sanitize(sd.provider.agent.config)
            data['provider']['agent']['config']['account_config'] = sanitize(sd.provider.agent.config.account_config)
            data['provider']['agent']['config']['group_config'] = sanitize(sd.provider.agent.config.group_config)
        elif self.provider_id == SAML_PROVIDER_ID:
            # TODO: Add this shit back in once I implement it in the underlying
            # Python library. For now we'll copy this stuff over manually.
            #data['provider']['attribute_statement_mapping_rules'] = sanitize(sd.provider.attribute_statement_mapping_rules)
            data['provider']['service_provider_metadata'] = sanitize(sd.provider.service_provider_metadata)

        # If the Directory already exists, we'll just update it.
        if dd:
            for key, value in data.iteritems():
                setattr(dd, key, value)

            while True:
                try:
                    dd.save()
                    return dd
                except StormpathError as err:
                    logger.error('Failed to copy destination Directory: {} ({})'.format(sd.name, err))

        # I'm manually setting the agent_user_dn_password field to a
        # random string here because our API won't export any
        # credentials, so it's impossible for me to migrate this over.
        if data.get('provider') and data.get('provider').get('agent'):
            data['provider']['agent']['config']['agent_user_dn_password'] = uuid4().hex

        # If we get here, it means we need to create the Directory from scratch.
        while True:
            try:
                return self.destination_client.directories.create(data)
            except StormpathError as err:
                logger.error('Failed to copy Directory: {} ({})'.format(sd.name, err))

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Directory.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        sd = self.source_directory
        dcd = self.destination_directory.custom_data

        for key, value in sanitize(sd.custom_data).items():
            dcd[key] = value

        while True:
            try:
                dcd.save()
                return dcd
            except StormpathError as err:
                logger.error('Failed to copy CustomData for Directory: {} ({})'.format(sd.name, err))

    def copy_strength(self):
        """
        Copy the Strength rules to the given Directory.

        :rtype: object (or None)
        :returns: The copied Strength, or None.
        """
        sd = self.source_directory
        ss = self.source_directory.password_policy.strength
        ds = self.destination_directory.password_policy.strength

        for field in ss.writable_attrs:
            ds[field] = ss[field]

        while True:
            try:
                ds.save()
                return ds
            except StormpathError as err:
                logger.error('Failed to copy Strength rules for Directory: {} ({})'.format(sd.name, err))

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
        self.destination_directory = self.get_destination_dir()
        self.destination_directory = self.copy_dir()
        self.copy_custom_data()

        # Mirror Directories don't support workflows at all, so this is moot.
        # What I'm doing here is returning immediately to avoid issues.
        if self.provider_id not in MIRROR_PROVIDER_IDS:
            self.copy_strength()

        logger.info('Successfully copied Directory: {}'.format(self.destination_directory.name))
        return self.destination_directory
