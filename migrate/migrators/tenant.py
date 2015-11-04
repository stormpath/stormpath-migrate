"""Our Tenant migrator."""


from . import *


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
        for directory in self.src.directories:
            if directory.name == 'Stormpath Administrators':
                continue

            migrator = DirectoryMigrator(destination_client=self.dst, source_directory=directory)
            destination_directory = migrator.migrate()

            for group in directory.groups:
                migrator = GroupMigrator(destination_directory=destination_directory, source_group=group)
                migrator.migrate()

            for account in directory.accounts:
                migrator = AccountMigrator(destination_directory=destination_directory, source_account=account, source_password='asfdasAFDAFDS!!!32423')
                migrator.migrate()

                for membership in account.group_memberships:
                    migrator = GroupMembershipMigrator(destination_client=self.dst, source_group_membership=membership)
                    migrator.migrate()

            migrator = DirectoryWorkflowMigrator(destination_directory=destination_directory, source_directory=directory)
            migrator.migrate()

        for organization in self.src.tenant.organizations:
            migrator = OrganizationMigrator(destination_client=self.dst, source_organization=organization)
            destination_organization = migrator.migrate()

            for mapping in organization.account_store_mappings:
                migrator = OrganizationAccountStoreMappingMigrator(destination_organization=destination_organization, source_account_store_mapping=mapping)
                migrator.migrate()

        for application in self.src.applications:
            if application.name == 'Stormpath':
                continue

            migrator = ApplicationMigrator(destination_client=self.dst, source_application=application)
            destination_application = migrator.migrate()

            for mapping in application.account_store_mappings:
                migrator = ApplicationAccountStoreMappingMigrator(destination_application=destination_application, source_account_store_mapping=mapping)
                migrator.migrate()
