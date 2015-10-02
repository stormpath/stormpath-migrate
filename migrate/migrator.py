"""Our migrator."""


from stormpath.client import Client


class Migrator(object):
    """
    This class manages a migration from one Stormpath Tenant to another.
    """
    def __init__(self, src, dst, from_date=None):
        self.src = src
        self.dst = dst
        self.from_date = from_date
        self._validate_credentials()

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

    def __repr__(self):
        return 'Migrator(<%s> -> <%s>)' % (self.src, self.dst)
