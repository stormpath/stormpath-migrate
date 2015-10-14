"""Our Directory Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class DirectoryMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Directory to another.
    """
    def get(self, href):
        """
        Retrieve the source Directory.

        :param str href: The source Directory href.
        :rtype: bool
        :returns: True if the Directory was successfully fetched, False
            otherwise.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to fetch Directory:', href

        try:
            self.src_dir = self.src.directories.get(href)
            return True
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch Directory:', href
            print err
            return False

    def copy(self):
        """
        Copy the source Directory over into the destination Tenant.

        :rtype: bool
        :returns: True if the Directory was successfully copied, False
            otherwise.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to copy Directory:', self.src_dir.name

        try:
            if dict(self.src_dir.provider).get('provider_id') != 'stormpath':
                self.dst_dir = self.dst.directories.create({
                    'description': self.src_dir.description,
                    'name': self.src_dir.name,
                    'provider': sanitize(self.src_dir.provider),
                    'status': self.src_dir.status,
                })
                return True
            else:
                self.dst_dir = self.dst.directories.create({
                    'description': self.src_dir.description,
                    'name': self.src_dir.name,
                    'status': self.src_dir.status,
                })
                return True
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Directory:', self.src_dir.name
            print err
            return False

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
        while not self.get(href):
            pass

        while not self.copy():
            pass
