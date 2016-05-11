"""Our Tenant migrator."""


from json import loads

from . import *


class TenantMigrator(BaseMigrator):
    """
    This class manages a migration from one Stormpath Tenant to another.
    """
    MIRROR_DIRECTORY_TYPES = ['ad', 'ldap']

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

            provider_id = dict(directory.provider).get('provider_id')

            if provider_id not in self.MIRROR_DIRECTORY_TYPES or provider_id == 'saml':
                for group in directory.groups:
                    migrator = GroupMigrator(destination_directory=destination_directory, source_group=group)
                    migrator.migrate()

            if provider_id not in self.MIRROR_DIRECTORY_TYPES and provider_id != 'saml':
                for account in directory.accounts:
                    hash = None
                    random_password = False

                    with open(self.passwords, 'rb') as f:
                        for raw_data in f:
                            data = loads(raw_data)

                            if data.get('href') == account.href:
                                hash = data.get('password')
                                break

                    if not hash:
                        random_password = True
                        print '[SOURCE] | [WARNING]: No password hash found for Account:', account.email, 'Using random password.'

                    migrator = AccountMigrator(destination_directory=destination_directory, source_account=account, source_password=hash, random_password=random_password)
                    migrated_account = migrator.migrate()

                    if not migrated_account:
                        continue

                    for group in account.groups:
                        migrator = GroupMembershipMigrator(destination_client=self.dst, destination_account=migrated_account, source_group=group)
                        migrator.migrate()

            if provider_id not in self.MIRROR_DIRECTORY_TYPES:
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

        migrator = SubstitutionMigrator(source_client=self.src, destination_client=self.dst)
        migrator.migrate()
