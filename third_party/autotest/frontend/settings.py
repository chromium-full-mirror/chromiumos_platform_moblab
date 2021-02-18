"""Django settings for frontend project.

Two databases are configured for the use with django here. One for tko tables,
which will always be the same database for all instances (the global database),
and one for everything else, which will be the same as the global database for
the primary, but a local database for shards.
Additionally there is a third database connection for read only access to the
global database.

This is implemented using a Django database router.
For more details on how the routing works, see db_router.py.
"""
DEBUG = False

FULL_ADMIN = False

ADMINS = ()

MANAGERS = ADMINS

ALLOWED_HOSTS = '*'

DATABASES = {
    'default': {
        'ENGINE': 'frontend.db.backends.afe',
        'PORT': '',
        'HOST': 'db',
        'NAME': 'chromeos_autotest_db',
        'USER': 'chromeosqa-admin',
        'PASSWORD': 'moblab_db_passwd',
        'OPTIONS': {'init_command':
                    "SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1;SET default_storage_engine=INNODB",
                    'isolation_level': 'read committed'
                   },
        'CONN_MAX_AGE': 3600
    }
}

TEMPLATES = [
]

# Have to set SECRET_KEY before importing connections because of this bug:
# https://code.djangoproject.com/ticket/20704
# TODO: Order this again after an upgrade to Django 1.6 or higher.
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'pn-t15u(epetamdflb%dqaaxw+5u&2#0u-jah70w1l*_9*)=n7'

# Do not do this here or from the router, or most unit tests will fail.
# from django.db import connection

DATABASE_ROUTERS = ['frontend.db_router.Router']

# prefix applied to all URLs - useful if requests are coming through apache,
# and you need this app to coexist with others
URL_PREFIX = 'afe/server/'
TKO_URL_PREFIX = 'new_tko/server/'

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'frontend.urls'

INSTALLED_APPS = (
    'frontend.afe',
    'frontend.tko',
)
