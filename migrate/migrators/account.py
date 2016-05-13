"""Our Account Migrator."""


from uuid import uuid4

from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
from ..utils import sanitize


class AccountMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Account to another.
    """
    RESOURCE = 'account'
    COLLECTION_RESOURCE = 'accounts'
    SOCIAL_PROVIDER_TYPES = ['facebook', 'google', 'linkedin', 'github']

    def __init__(self, destination_directory, source_account, source_password, random_password=False):
        self.destination_directory = destination_directory
        self.source_account = source_account
        self.source_password = source_password
        self.random_password = random_password

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        try:
            self.source_account.custom_data.refresh()
            return self.source_account.custom_data
        except StormpathError, err:
            logger.error('Could not fetch CustomData for source Account: {}: {}'.format(
                self.source_account.email,
                err
            ))

    def get_destination_account(self):
        """
        Retrieve the destination Account.

        :rtype: object (or None)
        :returns: The Account object, or None.
        """
        directory = self.destination_directory
        email = self.source_account.email

        while True:
            try:
                matches = directory.accounts.search({'email': email})
                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Account: {} in destination Directory: {}: {}'.format(email, directory.name, err))

    def copy_account(self):
        """
        Copy the source Account over into the destination Directory.

        :rtype: object (or None)
        :returns: The copied Account, or None.
        """
        data = {
            'username': self.source_account.username,
            'given_name': self.source_account.given_name,
            'middle_name': self.source_account.middle_name,
            'surname': self.source_account.surname,
            'email': self.source_account.email,
            'password': self.source_password,
            'status': self.source_account.status,
        }

        email = self.source_account.email
        name = self.destination_directory.name
        provider_data = dict(self.source_account.provider_data)
        provider_id = provider_data.get('provider_id')
        self.get_destination_account()

        if self.destination_account:
            # We don't support importing existing password hashes for
            # ALREADY existing user accounts, so we'll just skip the
            # password updating stuff here.
            del data['password']

            for key, value in data.iteritems():
                setattr(self.destination_account, key, value)

            try:
                self.destination_account.save()
            except StormpathError as err:
                logger.error('Could not update Account: {} in destination Directory: {}: {}'.format(email, name, err))
        else:
            if provider_id in self.SOCIAL_PROVIDER_TYPES:
                try:
                    self.destination_account = self.destination_directory.accounts.create({
                        'provider_data': {
                            'provider_id': provider_id,
                            'access_token': provider_data.access_token,
                        }
                    })
                except StormpathError as err:
                    logger.error('Could not create Account: {} in destination Directory: {}: {}'.format(email, name, err))
            elif provider_id == 'stormpath':
                if self.random_password:
                    data['password'] = uuid4().hex + uuid4().hex.upper() + '!'

                    try:
                        self.destination_account = self.destination_directory.accounts.create(data, registration_workflow_enabled=False)
                    except StormpathError as err:
                        logger.error('Could not create Account: {} in destination Directory: {}: {}'.format(email, name, err))
                else:
                    try:
                        self.destination_account = self.destination_directory.accounts.create(data, password_format='mcf', registration_workflow_enabled=False)
                    except StormpathError as err:
                        logger.error('Could not create Account: {} in destination Directory: {}: {}'.format(email, name, err))
            else:
                logger.info('Skipping Account creation for Account: {} in destination Directory: {} because Account is not a Cloud or Social Account.'.format(email, name))

        return self.destination_account

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
            logger.error('Could not copy CustomData for source Account: {} into destination Account: {}: {}'.format(
                self.source_account.email,
                self.destination_account.email,
                err
            ))

    def migrate(self):
        """
        Migrates one Account to another Tenant =)  Won't stop until the
        migration is complete.

        This will copy over the Account and Account meta data only -- it
        will not include any additional linked resources.

        :rtype: object (or None)
        :returns: The migrated Account, or None.
        """
        self.destination_account = self.get_destination_account()
        copied_account = self.copy_account()

        if copied_account:
            self.copy_custom_data()

            logger.info('Successfully copied source Account: {} into destination Directory: {}'.format(
                self.source_account.email,
                self.destination_directory.name
            ))
            return copied_account
        else:
            logger.error('Failed to copy source Account: {} into destination Directory: {}'.format(
                self.source_account.email,
                self.destination_directory.name
            ))
