"""Our Substitution Migrator."""


from . import BaseMigrator
from .. import logger


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
        sc = self.source_client
        dc = self.destination_client

        logger.info('Building index of Application HREFs... This may take a while.')
        for sa in sc.applications:
            self.hrefs[sa.href] = None

            for app in dc.applications.search({'name': sa.name}):
                self.hrefs[sa.href] = app.href

        logger.info('Building index of Directory HREFs... This may take a while.')
        for sd in sc.directories:
            self.hrefs[sd.href] = None

            for dir in dc.directories.search({'name': sd.name}):
                self.hrefs[sd.href] = dir.href

        logger.info('Building index of Organization HREFs... This may take a while.')
        for so in sc.tenant.organizations:
            self.hrefs[so.href] = None

            for org in dc.tenant.organizations.search({'name': so.name}):
                self.hrefs[so.href] = org.href

        logger.info('Building index of Group HREFs... This may take a while.')
        for sg in sc.groups:
            self.hrefs[sg.href] = None

            sd = sg.directory
            for dir in dc.directories.search({'name': sd.name}):
                for group in dir.groups.search({'name': sg.name}):
                    self.hrefs[sg.href] = group.href

        logger.info('Building index of Account HREFs... This may take a while.')
        for sd in sc.directories:
            for sa in sd.accounts:
                self.hrefs[sa.href] = None

                for dir in dc.directories.search({'name': sd.name}):
                    for account in dir.accounts.search({'email': sa.email}):
                        self.hrefs[sa.href] = account.href

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

                if isinstance(value, str) and value in self.hrefs:
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

                if isinstance(value, str) and value in self.hrefs:
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

                if isinstance(value, str) and value in self.hrefs:
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

                if isinstance(value, str) and value in self.hrefs:
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

                    if isinstance(value, str) and value in self.hrefs:
                        print 'Re-writing HREFs for Account:', acc.email
                        custom_data[key] = self.hrefs[value]
                        custom_data.save()
