"""Base Migrator class."""


from stormpath.client import Client
from stormpath.error import Error as StormpathError

from migrate.utils import sanitize


class BaseMigrator(object):
    """"
    This class provides a template for all other migrators.
    """
    def __init__(self, src, dst, from_date=None, verbose=False):
        self.src = src
        self.dst = dst
        self.from_date = from_date
        self.verbose = verbose

    def __repr__(self):
        return '%s()' % (self.__class__.__name__)

    def get_resource(self, href):
        """
        Retrieve the Resource from the source Tenant that is going to be
        migrated.

        :param str href: The Resource href.
        :rtype: object (or None)
        :returns: The Resource, or none.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to fetch %s: %s' % (RESOURCE.title(), href)

        try:
            return getattr(self.src, self.COLLECTION_RESOURCE).get(href)
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch %s: %s' % (RESOURCE.title(), href)
            print err

    def get_custom_data(self, resource):
        """
        Retrieve this Stormpath Resource's CustomData.

        :param obj resource: The Stormpath Resource.
        :rtype: object (or None)
        :returns: The CustomData, or None.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to fetch CustomData for Resource:', resource.href

        try:
            dict(resource.custom_data)
            return resource.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Resource:', resource.href
            print err

    def copy_custom_data(self, resource, custom_data):
        """
        Copy the Resource's CustomData over.

        :param obj resource: The Resource to store CustomData on.
        :param obj custom_data: The CustomData to copy.
        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        if self.verbose:
            print '[SOURCE]: Attempting to copy CustomData for Resource:', resource.href

        try:
            new_custom_data = resource.custom_data
            for key, value in sanitize(custom_data).iteritems():
                new_custom_data[key] = value

            new_custom_data.save()

            return new_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Resource:', resource.href
            print err

    def migrate(self):
        """
        Migrates one type of Stormpath resource =)  Won't stop until the
        migration is complete.

        NOTE: This may take a longggg time to run.
        """
        raise NotImplementedError('%s.migrate() must be defined.' % self.__class__.__name__)
