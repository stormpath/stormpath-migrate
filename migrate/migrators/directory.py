"""Our Directory Migrator."""


from uuid import uuid4

from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class DirectoryMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Directory to another.
    """
    RESOURCE = 'directory'
    COLLECTION_RESOURCE = 'directories'
    MIRROR_DIRECTORY_TYPES = ['ad', 'ldap']
    SOCIAL_DIRECTORY_TYPES = ['google', 'facebook', 'linkedin', 'github', 'saml']

    def __init__(self, destination_client, source_directory):
        self.destination_client = destination_client
        self.source_directory = source_directory
        self.destination_directory = None
        self.provider_id = dict(self.source_directory.provider).get('provider_id')

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
        matches = self.destination_client.directories.search({'name': self.source_directory.name.encode('utf-8')})
        if len(matches):
            self.destination_directory = matches[0]

        try:
            data = {
                'description': self.source_directory.description.encode('utf-8'),
                'name': self.source_directory.name.encode('utf-8'),
                'status': self.source_directory.status,
            }

            if self.provider_id != 'stormpath':
                data['provider'] = sanitize(self.source_directory.provider)

            if self.provider_id in self.MIRROR_DIRECTORY_TYPES:
                data['provider']['agent'] = sanitize(self.source_directory.provider.agent)
                data['provider']['agent']['config'] = sanitize(self.source_directory.provider.agent.config)
                data['provider']['agent']['config']['account_config'] = sanitize(self.source_directory.provider.agent.config.account_config)
                data['provider']['agent']['config']['group_config'] = sanitize(self.source_directory.provider.agent.config.group_config)

            if self.destination_directory:
                print 'Updating data for Directory:', self.source_directory.name.encode('utf-8')
                for key, value in data.iteritems():
                    setattr(self.destination_directory, key, value)

                self.destination_directory.save()
            else:
                # I'm manually setting the agent_user_dn_password field to a
                # random string here, because our API won't export any
                # credentials, so it's impossible for me to migrate this over.
                if data.get('provider') and data.get('provider').get('agent'):
                    data['provider']['agent']['config']['agent_user_dn_password'] = uuid4().hex

                self.destination_directory = self.destination_client.directories.create(data)

            return self.destination_directory
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Directory:', self.source_directory.name.encode('utf-8')
            print unicode(err).encode('utf-8')

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Directory.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
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
        copied_dir = self.copy_dir()
        self.copy_custom_data()

        # Mirror Directories don't support workflows at all, so this is moot.
        # What I'm doing here is returning immediately to avoid issues.
        if self.provider_id not in self.MIRROR_DIRECTORY_TYPES:
            self.copy_strength()

        print 'Successfully copied Directory:', copied_dir.name.encode('utf-8')
        return copied_dir
