"""Our Application Migrator."""


from stormpath.error import Error as StormpathError

from . import BaseMigrator
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
        self.destination_application = None

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            dict(self.source_application.custom_data)
            return self.source_application.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Application:', self.source_application.href
            print err

    def get_oauth_policy(self):
        """
        Retrieve the OAuthPolicy.

        :rtype: object (or None)
        :returns: The OAuthPolicy, or None.
        """
        try:
            oauth_policy = self.source_application.oauth_policy
            dict(oauth_policy)
            return oauth_policy
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch OAuthPolicy for Application:', self.source_application.href
            print err

    def copy_app(self):
        """
        Copy the source Application over into the destination Tenant.

        :rtype: object (or None)
        :returns: The copied Application, or None.
        """
        done = False
        while not done:
            try:
                self.destination_application = self.destination_client.applications.create({
                    'description': self.source_application.description,
                    'name': self.source_application.name,
                    'status': self.source_application.status,
                })
                return self.destination_application
            except StormpathError, err:
                if err.status == 409:
                    matches = len(self.destination_client.applications.search({'name': self.source_application.name}))
                    if not matches:
                        continue

                    to_delete = self.destination_client.applications.search({'name': self.source_application.name})[0]
                    try:
                        to_delete.delete()
                    except StormpathError, err:
                        continue

                    print 'Re-creating Application:', self.source_application.name
                    continue

                print '[SOURCE] | [ERROR]: Could not copy Application:', self.source_application.name
                print err

                done = True

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Application.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        try:
            source_custom_data = self.source_application.custom_data
            copied_custom_data = self.destination_application.custom_data

            for key, value in sanitize(source_custom_data).iteritems():
                copied_custom_data[key] = value

            copied_custom_data.save()
            return copied_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Application:', self.source_application.href
            print err

    def copy_oauth_policy(self):
        """
        Copy OAuthPolicy to the destination Application.

        :rtype: object (or None)
        :returns: The copied OAuthPolicy, or None.
        """
        try:
            source_oauth_policy = self.get_oauth_policy()
            destination_oauth_policy = self.destination_application.oauth_policy

            destination_oauth_policy.access_token_ttl = source_oauth_policy.access_token_ttl
            destination_oauth_policy.refresh_token_ttl = source_oauth_policy.refresh_token_ttl

            destination_oauth_policy.save()
            return destination_oauth_policy
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy OAuthPolicy for Application:', self.source_application.href
            print err

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
        copied_app = self.copy_app()
        self.copy_custom_data()
        self.copy_oauth_policy()

        print 'Successfully copied Application:', copied_app.name
        return copied_app
