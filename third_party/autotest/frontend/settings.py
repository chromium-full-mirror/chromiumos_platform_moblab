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

import common
from client.common_lib import global_config
from frontend import database_settings_helper

c = global_config.global_config
_section = 'AUTOTEST_WEB'

DEBUG = False

FULL_ADMIN = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

AUTOTEST_DEFAULT = database_settings_helper.get_default_db_config()
AUTOTEST_GLOBAL = database_settings_helper.get_global_db_config()
AUTOTEST_READONLY = database_settings_helper.get_readonly_db_config()
AUTOTEST_SERVER = database_settings_helper.get_server_db_config()

ALLOWED_HOSTS = '*'

DATABASES = {'default': AUTOTEST_DEFAULT,
             'global': AUTOTEST_GLOBAL,
             'readonly': AUTOTEST_READONLY,
             'server': AUTOTEST_SERVER,}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {'debug': True,
                    'loaders': ['django.template.loaders.filesystem.Loader',
                                'django.template.loaders.app_directories.Loader'
                               ]
                   }
    }
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix of static file. Only used by the admin interface.
STATIC_URL = '/' + URL_PREFIX + 'admin/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)

ROOT_URLCONF = 'frontend.urls'

INSTALLED_APPS = (
    'frontend.afe',
    'frontend.tko',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sites',
)
