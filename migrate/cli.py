"""
stormpath-migrate

Usage:
  stormpath-migrate <src> <dst> <passwords> [(-f <date> | --from <date>)] [(-v | --verbose)] [(-s <src-url> | --src-url <src-url>)] [(-d <dst-url> | --dst-url <dst-url>)]
  stormpath-migrate -h | --help
  stormpath-migrate --version

Options:
  -h --help                         Show this screen.
  -v --verbose                      Show verbose output.
  --version                         Show version.
  -f <date> | --from <date>         Only migrate resources created >= this date.  [ex: 2010-01-03]

Example:
  stormpath-migrate <id:secret> <id:secret>     # Migrate from src tenant to dst tenant.
  stormpath-migrate <id:secret> <id:secret> --from 2010-01-01
                                                # Migrate only resources from src tenant to dst tenant
                                                # created on or after 2010-01-01.

Help:
  For help using this tool, please contact Stormpath support:
  support@stormpath.com
"""


from docopt import docopt

from stormpath.client import Client

from . import __version__ as VERSION
from .migrators import TenantMigrator


def validate_credentials(src, dst):
    """
    Validate all user-specified credentials.

    Raises an error and stops processing if the credentials are not valid.

    :param str src: The user supplied Stormpath source credentials.
    :param str dst: The user supplied Stormpath destination credentials.
    :raises: ValueError on invalid credentials.
    """
    for val in [src, dst]:
        if len(val.split(':')) != 2:
            raise ValueError('Invalid credentials specified. Use <id:secret> format.')

        id, secret = val.split(':')
        if len(id) == 0 or len(secret) == 0:
            raise ValueError('Invalid credentials specified. Use <id:secret> format.')


def create_clients(src, dst, src_url, dst_url):
    """
    Create our local Stormpath Client objects used for the migration.

    :param str src: The user supplied Stormpath source credentials.
    :param str dst: The user supplied Stormpath destination credentials.
    :param str src_url: The Stormpath Base URL.
    :param str dst: The Stormpath Base URL.
    :rtype: tuple
    :returns: A tuple consisting of an initialized source Client object, as well
        as an initialized destination Client object.
    """
    src_id, src_secret = src.split(':')
    dst_id, dst_secret = dst.split(':')

    return (
        Client(id=src_id, secret=src_secret, base_url=src_url),
        Client(id=dst_id, secret=dst_secret, base_url=dst_url),
    )


def main():
    """Main CLI entrypoint."""
    args = docopt(__doc__, version=VERSION)

    src_url = args['<src-url>'] or 'https://api.stormpath.com/v1'
    dst_url = args['<dst-url>'] or 'https://api.stormpath.com/v1'

    validate_credentials(args['<src>'], args['<dst>'])
    clients = create_clients(args['<src>'], args['<dst>'], src_url=src_url, dst_url=dst_url)

    migrator = TenantMigrator(
        src = clients[0],
        dst = clients[1],
        passwords = args['<passwords>'],
        from_date = args['--from'],
        verbose = args['--verbose'],
    )
    migrator.migrate()
