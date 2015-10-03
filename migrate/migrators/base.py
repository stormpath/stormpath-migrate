"""Base Migrator class."""


from stormpath.client import Client


class BaseMigrator(object):
    """"
    This class provides a template for all other migrators.
    """
    def __init__(self, src, dst, from_date=None, verbose=False):
        self.src = src
        self.dst = dst
        self.from_date = from_date
        self._validate_credentials()
        self._create_clients()
        self.verbose = verbose

    def __repr__(self):
        return '%s(<%s> -> <%s>)' % (self.__class__.__name__, self.src, self.dst)

    def _validate_credentials(self):
        """
        Validate all user-specified credentials.

        Raises an error and stops processing if the credentials are not valid.
        """
        for val in [self.src, self.dst]:
            if len(val.split(':')) != 2:
                raise ValueError('Invalid credentials specified. Use ' \
                        '<id:secret> format.')

            id, secret = val.split(':')
            if len(id) == 0 or len(secret) == 0:
                raise ValueError('Invalid credentials specified. Use ' \
                        '<id:secret> format.')

    def _create_clients(self):
        """
        Create our local Stormpath Client objects used for the migration.
        """
        src_id, src_secret = self.src.split(':')
        dst_id, dst_secret = self.dst.split(':')

        self.src_client = Client(id=src_id, secret=src_secret)
        self.dst_client = Client(id=dst_id, secret=dst_secret)

    def migrate(self):
        """
        Migrates one type of Stormpath resource =)  Won't stop until the
        migration is complete.

        NOTE: This may take a longggg time to run.
        """
        raise NotImplementedError('%s.migrate() must be defined.' % self.__class__.__name__)
