import os, sys

path_list = ['/usr/local/autotest/site-packages',
             '/usr/local/autotest',
             '/usr/lib/python2.7/site-packages/autotest']

for p in path_list:
   if os.path.isdir(p):
       sys.path.append(p)

os.environ['DJANGO_SETTINGS_MODULE'] = 'frontend.settings'

from django.core.wsgi import get_wsgi_application

_application = get_wsgi_application()

def application(environ, start_response):
    environ['DJANGO_USE_POST_REWRITE'] = 'yes'
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    return _application(environ, start_response)
