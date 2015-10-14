"""Utility funtions."""


# A list of fields to sanitize.
FIELDS = ['created_at', 'href', 'modified_at', 'sp_http_status']


def sanitize(resource):
    """
    Validate all user-specified credentials.

    Sanitize a Stormpath resource, converting it to JSON, and removing all
    non-serializable data.

    :rtype: dict
    :returns: A sanitized object.
    """
    obj = dict(resource)
    for field in FIELDS:
        if obj.get(field):
            del obj[field]

    to_delete = []
    for key, value in obj.iteritems():
        if isinstance(value, object):
            to_delete.append(key)

    for key in to_delete:
        del obj[key]

    return obj
