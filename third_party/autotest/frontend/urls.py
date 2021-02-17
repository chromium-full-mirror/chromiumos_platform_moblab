from django.conf.urls import url
from django.conf.urls import include

from frontend.afe import views


RE_PREFIX = '^' + settings.URL_PREFIX
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'frontend.afe.views.handler500'

urlpatterns = [
        url(RE_PREFIX, include('frontend.afe.urls')),
]

