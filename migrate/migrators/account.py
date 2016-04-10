"""Our Account Migrator."""


from uuid import uuid4

from stormpath.error import Error as StormpathError

from . import BaseMigrator
from ..utils import sanitize


class AccountMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Account to another.
    """
    RESOURCE = 'account'
    COLLECTION_RESOURCE = 'accounts'

    def __init__(self, destination_directory, source_account, source_password, random_password=False):
        self.destination_directory = destination_directory
        self.source_account = source_account
        self.source_password = source_password
        self.destination_account = None
        self.random_password = random_password

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            dict(self.source_account.custom_data)
            return self.source_account.custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not fetch CustomData for Account:', self.source_account.href
            print err

    def copy_account(self):
        """
        Copy the source Account over into the destination Directory.

        :rtype: object (or None)
        :returns: The copied Account, or None.
        """
        matches = self.destination_directory.accounts.search({'email': self.source_account.email})
        if len(matches):
            self.destination_account = matches[0]

        data = {
            'username': self.source_account.username,
            'given_name': self.source_account.given_name,
            'middle_name': self.source_account.middle_name,
            'surname': self.source_account.surname,
            'email': self.source_account.email,
            'password': self.source_password,
            'status': self.source_account.status,
        }

        try:
            if dict(self.source_account.provider_data).get('provider_id') != 'stormpath' and not self.destination_account:
                self.destination_account = self.destination_directory.accounts.create({
                    'provider_data': {
                        'provider_id': self.source_account.provider_data.provider_id,
                        'access_token': self.source_account.provider_data.access_token,
                    }
                }, registration_workflow_enabled=False)
            elif self.destination_account:
                print 'Updating data for Account:', self.source_account.email

                # We don't support importing existing password hashes for
                # ALREADY existing user accounts, so we'll just skip the
                # password updating stuff here.
                del data['password']

                for key, value in data.iteritems():
                    setattr(self.destination_account, key, value)

                self.destination_account.save()
            else:
                if not self.random_password:
                    self.destination_account = self.destination_directory.accounts.create(data, password_format='mcf', registration_workflow_enabled=False)
                else:
                    data['password'] = uuid4().hex + uuid4().hex.upper() + '!'
                    self.destination_account = self.destination_directory.accounts.create(data, registration_workflow_enabled=False)

            return self.destination_account
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy Account:', self.source_account.email
            print err

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Account.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        try:
            source_custom_data = self.source_account.custom_data
            if not source_custom_data:
                return

            if not self.destination_account:
                return

            copied_custom_data = self.destination_account.custom_data

            for key, value in sanitize(source_custom_data).iteritems():
                copied_custom_data[key] = value

            copied_custom_data.save()
            return copied_custom_data
        except StormpathError, err:
            print '[SOURCE] | [ERROR]: Could not copy CustomData for Account:', self.source_account.href
            print err

    def migrate(self):
        """
        Migrates one Account to another Tenant =)  Won't stop until the
        migration is complete.

        This will copy over the Account and Account meta data only -- it
        will not include any additional linked resources.

        :rtype: object (or None)
        :returns: The migrated Account, or None.
        """
        copied_account = self.copy_account()
        if copied_account:
            self.copy_custom_data()

            print 'Successfully copied Account:', copied_account.email
            return copied_account
