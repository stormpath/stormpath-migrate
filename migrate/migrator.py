"""Our migrator."""


class Migrator(object):
    """
    This class manages a migration from one Stormpath Tenant to another.
    """
    def __init__(self, src, dst, from_date=None):
        self.src = src
        self.dst = dst
        self.from_date = from_date

    def __repr__(self):
        return 'Migrator(<%s> -> <%s>)' % (self.src, self.dst)
