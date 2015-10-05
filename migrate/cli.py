"""
stormpath-migrate

Usage:
  stormpath-migrate <src> <dst> [(-f <date> | --from <date>)] [(-v | --verbose)]
  stormpath-migrate -h | --help
  stormpath-migrate --version

Options:
  -h --help                         Show this screen.
  -v --verbose                      Show verbose output.
  --version                         Show version.
  -i <id> | --id <id>               Stormpath API key id.
  -s <secret> | --secret <secret>   Stormpath API key secret.
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


def create_clients(src, dst):
    """
    Create our local Stormpath Client objects used for the migration.

    :param str src: The user supplied Stormpath source credentials.
    :param str dst: The user supplied Stormpath destination credentials.
    :rtype: tuple
    :returns: A tuple consisting of an initialized source Client object, as well
        as an initialized destination Client object.
    """
    src_id, src_secret = src.split(':')
    dst_id, dst_secret = dst.split(':')

    return (
        Client(id=src_id, secret=src_secret),
        Client(id=dst_id, secret=dst_secret),
    )


def main():
    """Main CLI entrypoint."""
    args = docopt(__doc__, version=VERSION)

    validate_credentials(src, dst)
    clients = create_clients(src, dst)

    migrator = TenantMigrator(
        src = clients[0],
        dst = clients[1],
        from_date = args['--from'],
        verbose = args['--verbose'],
    )
