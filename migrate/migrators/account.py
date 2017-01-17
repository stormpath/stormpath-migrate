"""Our Account Migrator."""


from uuid import uuid4

from stormpath.error import Error as StormpathError

from . import BaseMigrator
from .. import logger
from ..constants import SOCIAL_PROVIDER_IDS
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
        self.random_password = random_password

    def get_custom_data(self):
        """
        Retrieve the CustomData.

        :rtype: object (or None)
        :returns: The CustomData object, or None.
        """
        sa = self.source_account

        while True:
            try:
                sa.custom_data.refresh()
                return sa.custom_data
            except StormpathError as err:
                logger.error('Failed to fetch CustomData for source Account: {} ({})'.format(sa.username.encode('utf-8'), err))

    def get_destination_account(self):
        """
        Retrieve the destination Account.

        :rtype: object (or None)
        :returns: The Account object, or None.
        """
        directory = self.destination_directory
        username = self.source_account.username
        email = self.source_account.email

        while True:
            try:
                matches = directory.accounts.search({'username': username})

                if len(matches) == 0:
                    matches = directory.accounts.search({'email': email})

                return matches[0] if len(matches) > 0 else None
            except StormpathError as err:
                logger.error('Failed to search for Account: {} in destination Directory: {} ({})'.format(username.encode('utf-8'), directory.name.encode('utf-8'), err))

    def copy_account(self):
        """
        Copy the source Account over into the destination Directory.

        :rtype: object (or None)
        :returns: The copied Account, or None.
        """
        sa = self.source_account
        da = self.destination_account
        dd = self.destination_directory

        data = {
            'username': sa.username,
            'given_name': sa.given_name,
            'middle_name': sa.middle_name,
            'surname': sa.surname,
            'email': sa.email,
            'password': self.source_password,
            'status': sa.status,
        }

        provider_data = dict(sa.provider_data)
        provider_id = provider_data.get('provider_id')

        # If the Account already exists in the destination Directory, then we
        # simply need to update its data.
        if da:
            # We don't support importing existing password hashes for
            # ALREADY existing user accounts, so we'll just skip the
            # password updating stuff here.
            del data['password']

            for key, value in data.items():
                setattr(da, key, value)

            while True:
                try:
                    da.save()
                    return da
                except StormpathError as err:
                    logger.error('Failed to update Account: {} in destination Directory: {} ({})'.format(sa.username.encode('utf-8'), dd.name.encode('utf-8'), err))

        # If we get here, it means the Account needs to be created in the
        # destination Directory.
        if provider_id in SOCIAL_PROVIDER_IDS:
            while True:
                try:
                    da = dd.accounts.create({
                        'provider_data': {
                            'provider_id': provider_id,
                            'access_token': dict(provider_data)['access_token'],
                        }
                    })
                    return da
                except StormpathError as err:
                    logger.error('Failed to create {} Account: {} in destination Directory: {} ({})'.format(provider_id.title(), sa.username.encode('utf-8'), dd.name.encode('utf-8'), err))
                    break

        elif provider_id == 'stormpath':
            if self.random_password:
                data['password'] = uuid4().hex + uuid4().hex.upper() + '!'

                while True:
                    try:
                        da = dd.accounts.create(data, registration_workflow_enabled=False)
                        return da
                    except StormpathError as err:
                        logger.error('Failed to create Account: {} in destination Directory: {} ({})'.format(sa.username.encode('utf-8'), dd.name.encode('utf-8'), err))

            # If we get here, if means we're going to use a pre-existing
            # password hash to create this Account.
            while True:
                try:
                    da = dd.accounts.create(data, password_format='mcf', registration_workflow_enabled=False)
                    return da
                except StormpathError as err:
                    logger.error('Failed to create Account: {} in destination Directory: {} ({})'.format(sa.username.encode('utf-8'), dd.name.encode('utf-8'), err))

        else:
            logger.warning('Skipping {} Account creation for Account: {} in destination Directory: {} because Account is not a Cloud or Social Account.'.format(provider_id.upper(), da.username.encode('utf-8'), dd.name.encode('utf-8')))

    def copy_custom_data(self):
        """
        Copy CustomData to the destination Account.

        :rtype: object (or None)
        :returns: The copied CustomData, or None.
        """
        sa = self.source_account
        da = self.destination_account

        for key, value in sanitize(self.get_custom_data()).items():
            da.custom_data[key] = value

        while True:
            try:
                da.custom_data.save()
                return da.custom_data
            except StormpathError as err:
                logger.error('Failed to copy CustomData for source Account: {} into destination Account: {} ({})'.format(sa.username.encode('utf-8'), da.username.encode('utf-8'), err))

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
        self.destination_account = self.copy_account()

        sa = self.source_account
        dd = self.destination_directory

        if self.destination_account:
            self.copy_custom_data()
            logger.info('Successfully copied Account: {} into destination Directory: {}'.format(sa.username.encode('utf-8'), dd.name.encode('utf-8')))

            return self.destination_account
        else:
            logger.warning('Not copying Account: {} into destination Directory: {}'.format(sa.username.encode('utf-8'), dd.name.encode('utf-8')))
