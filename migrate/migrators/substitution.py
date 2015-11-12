"""Our Substitution Migrator."""


from . import BaseMigrator


class SubstitutionMigrator(BaseMigrator):
    """
    This class manages a migration of all HREFs (inside CustomData) from one
    Tenant to Another.
    """
    def __init__(self, source_client, destination_client):
        self.source_client = source_client
        self.destination_client = destination_client
        self.hrefs = {}

    def build_hrefs(self):
        """
        Build an index of HREFs that we can use for substitutions later on.
        """
        print 'Building index of Application HREFs.'
        for source_application in self.source_client.applications:
            self.hrefs[source_application.href] = None

            for app in self.destination_client.applications.search({'name': source_application.name}):
                self.hrefs[source_application.href] = app.href

        print 'Building index of Directory HREFs.'
        for source_directory in self.source_client.directories:
            self.hrefs[source_directory.href] = None

            for dir in self.destination_client.directories.search({'name': source_directory.name}):
                self.hrefs[source_directory.href] = dir.href

        print 'Building index of Organization HREFs.'
        for source_organization in self.source_client.tenant.organizations:
            self.hrefs[source_organization.href] = None

            for org in self.destination_client.tenant.organizations.search({'name': source_organization.name}):
                self.hrefs[source_organization.href] = org.href

        print 'Building index of Group HREFs.'
        for source_group in self.source_client.groups:
            self.hrefs[source_group.href] = None

            source_directory = source_group.directory
            for dir in self.destination_client.directories.search({'name': source_directory.name}):
                for group in dir.groups.search({'name': source_group.name}):
                    self.hrefs[source_group.href] = group.href

        print 'Building index of Account HREFs.'
        for source_directory in self.source_client.directories:
            for source_account in source_directory.accounts:
                self.hrefs[source_account.href] = None

                for dir in self.destination_client.directories.search({'name': source_directory.name}):
                    for account in dir.accounts.search({'email': source_account.email}):
                        self.hrefs[source_account.href] = account.href

    def migrate(self):
        """
        Rewrites all HREFs.
        """
        self.build_hrefs()

        for app in self.destination_client.applications:
            custom_data = app.custom_data

            for key, value in dict(custom_data).iteritems():
                if key in self.hrefs and self.hrefs[key]:
                    print 'Re-writing HREFs for Application:', app.name
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value
                    custom_data.save()

                if value in self.hrefs:
                    print 'Re-writing HREFs for Application:', app.name
                    custom_data[key] = self.hrefs[value]
                    custom_data.save()

        for dir in self.destination_client.directories:
            custom_data = dir.custom_data

            for key, value in dict(custom_data).iteritems():
                if key in self.hrefs and self.hrefs[key]:
                    print 'Re-writing HREFs for Directory:', dir.name
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value
                    custom_data.save()

                if value in self.hrefs:
                    print 'Re-writing HREFs for Directory:', dir.name
                    custom_data[key] = self.hrefs[value]
                    custom_data.save()

        for org in self.destination_client.tenant.organizations:
            custom_data = org.custom_data

            for key, value in dict(custom_data).iteritems():
                if key in self.hrefs and self.hrefs[key]:
                    print 'Re-writing HREFs for Directory:', dir.name
                    print 'Re-writing HREFs for Organization:', org.name
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value
                    custom_data.save()

                if value in self.hrefs:
                    print 'Re-writing HREFs for Organization:', org.name
                    custom_data[key] = self.hrefs[value]
                    custom_data.save()

        for group in self.destination_client.groups:
            custom_data = group.custom_data

            for key, value in dict(custom_data).iteritems():
                if key in self.hrefs and self.hrefs[key]:
                    print 'Re-writing HREFs for Group:', group.name
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value
                    custom_data.save()

                if value in self.hrefs:
                    print 'Re-writing HREFs for Group:', group.name
                    custom_data[key] = self.hrefs[value]
                    custom_data.save()

        for directory in self.destination_client.directories:
            for acc in directory.accounts:
                custom_data = acc.custom_data

                for key, value in dict(custom_data).iteritems():
                    if key in self.hrefs and self.hrefs[key]:
                        print 'Re-writing HREFs for Account:', acc.email
                        del custom_data[key]
                        custom_data[self.hrefs[key]] = value
                        custom_data.save()

                    if value in self.hrefs:
                        print 'Re-writing HREFs for Account:', acc.email
                        custom_data[key] = self.hrefs[value]
                        custom_data.save()
