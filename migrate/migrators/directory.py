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

    def get_strength(self, dir):
        """
        Retrieve the Strength.

        :rtype: object (or None)
        :returns: The Strength, or None.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to fetch Strength for Directory:', dir.href

        try:
            strength = dir.password_policy.strength
            dict(strength)
            return strength
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch Strength for Directory:', dir.href
            print err

    def copy_strength(self, dir, strength):
        """
        Copy the Strength rules to the given Directory.

        :param obj dir: The Directory to use.
        :param obj strength: The Strength to copy.
        :rtype: object (or None)
        :returns: The copied Strength, or None.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to copy Strength rules for Directory:', dir.name

        try:
            copied_strength = dir.password_policy.strength
            for field in copied_strength.writable_attrs:
                copied_strength[field] = strength[field]

            copied_strength.save()

            return copied_strength
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Directory:', dir.name
            print err

    def copy_dir(self, dir):
        """
        Copy the source Directory over into the destination Tenant.

        :param obj dir: The Directory to copy.
        :rtype: object (or None)
        :returns: The copied Directory, or None.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to copy Directory:', dir.name

        try:
            data = {
                'description': dir.description,
                'name': dir.name,
                'status': dir.status,
            }

            if dict(dir.provider).get('provider_id') != 'stormpath':
                data['provider'] = sanitize(dir.provider)

            return self.dst.directories.create(data)
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Directory:', dir.name
            print err

    def migrate(self, href):
        """
        Migrates one Directory to another Tenant =)  Won't stop until the
        migration is complete.

        This will copy over the Directory and Directory meta data only -- it
        will not include any Workflow settings.  This is done because Workflows
        need to be migrated separately after Accounts have been migrated -- this
        way we avoid emailing users unnecessarily when a Directory has Workflows
        enabled.

        :param str href: The href of the source Directory to copy.
        """
        dir, custom_data, strength, dst_dir = None

        while not dir:
            dir = self.get_resource(href)

        while not custom_data:
            custom_data = self.get_custom_data(dir)

        while not strength:
            strength = self.get_strength(dir)

        while not dst_dir:
            dst_dir = self.copy_dir(dir=dir, password_policy=password_policy)

        while not self.copy_custom_data(resource=dst_dir, custom_data=custom_data):
            continue
