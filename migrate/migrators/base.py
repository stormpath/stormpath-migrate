"""Base Migrator class."""


from .. import logger


class BaseMigrator(object):
    """"
    This class provides a template for all other migrators.
    """
    def __init__(self, src, dst, passwords, from_date=None, verbose=False):
        self.log = logger
        self.src = src
        self.dst = dst
        self.passwords = passwords
        self.from_date = from_date
        self.verbose = verbose

    def __repr__(self):
        return '%s()' % (self.__class__.__name__)

    def migrate(self):
        """
        Migrates one type of Stormpath resource =)  Won't stop until the
        migration is complete.

        NOTE: This may take a longggg time to run.
        """
        raise NotImplementedError('%s.migrate() must be defined.' % self.__class__.__name__)
