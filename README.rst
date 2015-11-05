stormpath-migrate
=================

*Migrate a Stormpath tenant from one place to another.*


Installation
------------

To install this library, use Pip::

    $ pip install stormpath-migrate


Usage
-----

To use this tool, you need a few things:

- A newline delimited JSON file that contains JSON objects that look like: ``{"href": "account_href", "password": "password_hash"}``.
- A pair of Stormpath API keys for the SOURCE tenant you want to migrate.
- The Stormpath Base URL for the SOURCE tenant you want to migrate.
- A pair of Stormpath API keys for the DESTINATION tenant you want to migrate.
- The Stormpath Base URL for the DESTINATION tenant you want to migrate.

Once you have these things, we can begin.

Let's say that I have two Stormpath Tenants, with the following API keys and
Base URLs, respectively:

- SOURCE: xxx:yyy https://api.stormpath.com/v1
- DESTINATION: blah:blah https://test.stormpath.io/v1

Let's also say I have the properly exported my existing user passwords by
talking with the Stormpath engineering team, and have a file named
``passwords.txt`` which contains my JSON delimited data.

I could then run the following command to properly migrate all of my data from
the SOURCE tenant to the DESTINATION tenant::

    $ stormpath-migrate 'xxx:yyy' 'blah:blah' passwords.txt \
        --src-url https://api.stormpath.com/v1
        --dst-url https://test.stormpath.io/v1

This will initialize the migration process, and will output to the terminal with
progress reports. Depending on how many resource you have in your Stormpath
tenant, this may take a very long time.

This program should be run on a computer with a strong and consistent internet
connection for the best results.

This program can be run multiple times in a row to perform incremental backups.
Objects will NOT be deleted from the DESTINATION tenant. They will only be
copied over from the SOURCE tenant.
