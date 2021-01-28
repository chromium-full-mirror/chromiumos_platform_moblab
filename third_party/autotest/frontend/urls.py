import os
from django.conf.urls import url
from django.conf.urls import include
from django.conf import settings

from frontend.afe import views

# The next two lines enable the admin and load each admin.py file:
from django.contrib import admin
admin.autodiscover()

RE_PREFIX = '^' + settings.URL_PREFIX
TKO_RE_PREFIX = '^' + settings.TKO_URL_PREFIX

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'frontend.afe.views.handler500'

urlpatterns = [
        url(RE_PREFIX + r'admin/', admin.site.urls),
        url(RE_PREFIX, include('frontend.afe.urls')),
        url(TKO_RE_PREFIX, include('frontend.tko.urls')),
]

if os.path.exists(os.path.join(os.path.dirname(__file__),
                               'tko', 'site_urls.py')):
    urlpatterns += [
            url(TKO_RE_PREFIX, include('frontend.tko.site_urls'))
            ]

debug_patterns = [
        # redirect /tko and /results to local apache server
        url(r'^(?P<path>(tko|results)/.*)$',
            views.redirect_with_extra_data,
            {'url': 'http://%(server_name)s/%(path)s?%(getdata)s'}),
]

if settings.DEBUG:
    urlpatterns += debug_patterns
