from django.conf.urls import url
import common
from frontend import settings, urls_common
from frontend.tko import views

urlpatterns, debug_patterns = (
        urls_common.generate_patterns('frontend.tko', 'TkoClient'))

urlpatterns += [
        url(r'^(?:|noauth/)jsonp_rpc/', views.handle_jsonp_rpc),
        url(r'^(?:|noauth/)csv/', views.handle_csv),
        url(r'^(?:|noauth/)plot/', views.handle_plot)
]


if settings.DEBUG:
    urlpatterns += debug_patterns
