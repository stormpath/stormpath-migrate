"""Our Application Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
from ..utils import sanitize


class ApplicationMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Application to another.
    """
    RESOURCE = 'application'
    COLLECTION_RESOURCE = 'applications'

    def __init__(self, destination_client, source_application):
        self.destination_client = destination_client
        self.source_application = source_application

    def get_destination_app(self):
        """
        Retrieve the destination Application.

        :rtype: object (or None)
        :returns: The Application object, or None.
        """
        sa = self.source_application

        while True:
            try:
                matches = self.destination_client.applications.search({'name': sa.name})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Application: {} ({})'.format(sa.name, err))

    def copy_app(self):
        """
        Copy the source Application over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Application, or None.
        """
        sa = self.source_application
        da = self.destination_application

        data = {
            'description': sa.description,
            'name': sa.name,
            'status': sa.status,
        }

        # If the Application already exists, we'll just update it.
        if da:
            for key, value in data.items():
                setattr(da, key, value)

            while True:
                try:
                    da.save()
                    return da
                except StormpathError as err:
                    logger.error('Failed to copy Application: {} ({})'.format(sa.name, err))

        # If we get here, it means we need to create the Application from
        # scratch.
        while True:
            try:
                return self.destination_client.applications.create(data)
            except StormpathError as err:
                logger.error('Failed to copy Application: {} ({})'.format(sa.name, err))

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Application.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        sa = self.source_application
        da = self.destination_application

        for key, value in sanitize(sa.custom_data).items():
            da.custom_data[key] = value

        while True:
            try:
                da.custom_data.save()
                return da.custom_data
            except StormpathError as err:
                logger.error('Failed to copy CustomData for source Application: {} into destination Account: {} ({})'.format(sa.name, da.name, err))

    def copy_oauth_policy(self):
        """
        Copy OAuthPolicy to the destination Application.

        :rtype: object (or None)
        :returns: The copied OAuthPolicy, or None.
        """
        sa = self.source_application
        da = self.destination_application

        sop = sa.oauth_policy
        dop = da.oauth_policy

        dop.access_token_ttl = sop.access_token_ttl
        dop.refresh_token_ttl = sop.refresh_token_ttl

        while True:
            try:
                dop.save()
                return dop
            except StormpathError as err:
                logger.error('Failed to copy OAuthPolicy for Application: {} ({})'.format(sa.name, err))

    def migrate(self):
        """
        Migrates one Application to another Tenant =)  Won't stop until the
        migration is complete.

        This will copy over the Application and Application meta data only -- it
        will not include any Account Stores.  This is done because Account
        Stores will be migrated separately after they've all been copied over.

        :rtype: object (or None)
        :returns: The migrated Application, or None.
        """
        self.destination_application = self.get_destination_app()
        self.destination_application = self.copy_app()
        self.copy_custom_data()
        self.copy_oauth_policy()

        logger.info('Successfully copied Application: {}'.format(self.destination_application.name))
        return self.destination_application
