"""Our Substitution Migrator."""


from csv import QUOTE_ALL, writer

from stormpath.error import Error as StormpathError

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

        logger.info('Starting to build index of Stormpath Resource HREFs... This may take a while.')

        for sa in sc.applications:
            self.hrefs[sa.href] = None

            for app in dc.applications.search({'name': sa.name}):
                self.hrefs[sa.href] = app.href

        logger.info('Finished building index of Application HREFs.')

        for sd in sc.directories:
            self.hrefs[sd.href] = None

            for dir in dc.directories.search({'name': sd.name}):
                self.hrefs[sd.href] = dir.href

        logger.info('Finished building index of Directory HREFs.')

        for so in sc.tenant.organizations:
            self.hrefs[so.href] = None

            for org in dc.tenant.organizations.search({'name': so.name}):
                self.hrefs[so.href] = org.href

        logger.info('Finished building index of Organization HREFs.')

        for sg in sc.groups:
            self.hrefs[sg.href] = None

            sd = sg.directory
            for dir in dc.directories.search({'name': sd.name}):
                for group in dir.groups.search({'name': sg.name}):
                    self.hrefs[sg.href] = group.href

        logger.info('Finished building index of Group HREFs.')

        for sd in sc.directories:
            for sa in sd.accounts:
                self.hrefs[sa.href] = None

                for dir in dc.directories.search({'name': sd.name}):
                    for account in dir.accounts.search({'email': sa.email}):
                        self.hrefs[sa.href] = account.href

        logger.info('Finished building index of Account HREFs.')

    def output_hrefs(self):
        """
        Output a CSV file with both the OLD resource HREFs, and the NEW resource
        HREFs.  This is useful when a client has their database linked to
        Stormpath HREFs, as it gives them a way to pragmatically update their
        database HREFs as necessary.
        """
        logger.info('Generating CSV file of migrated resource mappings.')

        with open('stormpath-mappings.csv', 'wb') as csvfile:
            csv_writer = writer(csvfile, delimiter=',', quotechar='"', quoting=QUOTE_ALL)
            csv_writer.writerow(['original_href', 'migrated_href'])

            for old_href, new_href in self.hrefs.items():
                csv_writer.writerow([old_href, new_href])

        logger.info('Finished generating CSV file of migrated resource mappings.')

    def rewrite_hrefs(self):
        """
        Rewrite all hrefs.

        :returns: None
        """
        dc = self.destination_client

        for app in dc.applications:
            custom_data = app.custom_data

            for key, value in dict(custom_data).items():
                if key in self.hrefs and self.hrefs[key]:
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Application: {}'.format(app.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Application: {} ({})'.format(app.name, err))

                if isinstance(value, str) and value in self.hrefs:
                    custom_data[key] = self.hrefs[value]

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Application: {}'.format(app.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Application: {} ({})'.format(app.name, err))

        for dir in dc.directories:
            custom_data = dir.custom_data

            for key, value in dict(custom_data).items():
                if key in self.hrefs and self.hrefs[key]:
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Directory: {}'.format(dir.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Directory: {} ({})'.format(dir.name, err))

                if isinstance(value, str) and value in self.hrefs:
                    custom_data[key] = self.hrefs[value]

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Directory: {}'.format(dir.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Directory: {} ({})'.format(dir.name, err))

        for org in dc.tenant.organizations:
            custom_data = org.custom_data

            for key, value in dict(custom_data).items():
                if key in self.hrefs and self.hrefs[key]:
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Organization: {}'.format(org.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Organization: {} ({})'.format(org.name, err))

                if isinstance(value, str) and value in self.hrefs:
                    custom_data[key] = self.hrefs[value]

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Organization: {}'.format(org.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Organization: {} ({})'.format(org.name, err))

        for group in dc.groups:
            custom_data = group.custom_data

            for key, value in dict(custom_data).items():
                if key in self.hrefs and self.hrefs[key]:
                    del custom_data[key]
                    custom_data[self.hrefs[key]] = value

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Group: {}'.format(group.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Group: {} ({})'.format(group.name, err))

                if isinstance(value, str) and value in self.hrefs:
                    custom_data[key] = self.hrefs[value]

                    while True:
                        try:
                            custom_data.save()
                            logger.info('Successfully rewrote HREF for Group: {}'.format(group.name))
                        except StormpathError as err:
                            logger.error('Failed to rewrite HREF for Group: {} ({})'.format(group.name, err))

        for directory in dc.directories:
            for acc in directory.accounts:
                custom_data = acc.custom_data

                for key, value in dict(custom_data).items():
                    if key in self.hrefs and self.hrefs[key]:
                        del custom_data[key]
                        custom_data[self.hrefs[key]] = value

                        while True:
                            try:
                                custom_data.save()
                                logger.info('Successfully rewrote HREF for Account: {}'.format(acc.username))
                            except StormpathError as err:
                                logger.error('Failed to rewrite HREF for Account: {} ({})'.format(acc.username, err))

                    if isinstance(value, str) and value in self.hrefs:
                        custom_data[key] = self.hrefs[value]

                        while True:
                            try:
                                custom_data.save()
                                logger.info('Successfully rewrote HREF for Account: {}'.format(acc.username))
                            except StormpathError as err:
                                logger.error('Failed to rewrite HREF for Account: {} ({})'.format(acc.username, err))

    def migrate(self):
        """
        Rewrites all HREFs.
        """
        self.build_hrefs()
        self.output_hrefs()
        self.rewrite_hrefs()
