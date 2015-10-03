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

from . import __version__ as VERSION
from .migrators import TenantMigrator


def main():
    args = docopt(__doc__, version=VERSION)
    migrator = TenantMigrator(
        src = args['<src>'],
        dst = args['<dst>'],
        from_date = args['--from']
    )
