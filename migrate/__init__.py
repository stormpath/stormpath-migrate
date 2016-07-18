"""Migrate module."""


from logging import DEBUG, Formatter, StreamHandler, getLogger


__version__ = '1.1.3'


# Global logger object.  Used for controlling program output.
logger = getLogger(__name__)
logger.setLevel(DEBUG)

log_handler = StreamHandler()
log_handler.setLevel(DEBUG)

formatter = Formatter('%(name)s[%(module)s][%(levelname)s]: %(message)s')
log_handler.setFormatter(formatter)

logger.addHandler(log_handler)
