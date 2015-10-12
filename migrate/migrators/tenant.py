"""Our Tenant migrator."""


from . import BaseMigrator, DirectoryMigrator


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
        for directory in self.src_client.directories:
            directory_migrator = DirectoryMigrator(
                src = self.src,
                dst = self.dst,
                from_date = self.from_date,
                verbose = self.verbose,
                href = directory.href,
            )
            directory_migrator.migrate()
