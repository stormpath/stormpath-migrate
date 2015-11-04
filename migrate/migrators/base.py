"""Base Migrator class."""


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

    def migrate(self):
        """
        Migrates one type of Stormpath resource =)  Won't stop until the
        migration is complete.

        NOTE: This may take a longggg time to run.
        """
        raise NotImplementedError('%s.migrate() must be defined.' % self.__class__.__name__)
