from django.conf import urls
from frontend import settings, urls_common

urlpatterns, debug_patterns = (
        urls_common.generate_patterns('frontend.afe', 'AfeClient'))

