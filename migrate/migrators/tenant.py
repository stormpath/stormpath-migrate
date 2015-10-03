"""Our Tenant migrator."""


from . import BaseMigrator


class TenantMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Tenant to another.
    """
    def migrate(self):
        """
        Migrates one Tenant to another =)  Won't stop until the migration is
        complete.

        NOTE: This may take a longggg time to run.
        """
        pass
