import os
from django.conf.urls import url
from django.views import generic
from django.views import static
from frontend.afe import views as afe_views


def generate_patterns(django_name, gwt_name):
    """
    Generates the common URL patterns for the given names

    @param django_name the full name of the Django application
                       (e.g., frontend.afe)
    @param gwt_name the name of the GWT project (e.g., AfeClient)
    @return the common standard and the debug pattern lists, as a tuple
    """
    pattern_list = [
            url(r'^(?:|noauth/)rpc/', afe_views.handle_rpc),
            url(r'^rpc_doc', afe_views.rpc_documentation),
    ]

    debug_pattern_list = [
            # for GWT hosted mode
            url(r'^(?P<forward_addr>autotest.*)',
                afe_views.gwt_forward),

            # for GWT compiled files
            url(r'^client/(?P<path>.*)$', static.serve,
                {'document_root': os.path.join(os.path.dirname(__file__), '..',
                                               'frontend', 'client', 'www')}),
            # redirect / to compiled client
            url(r'^$', generic.RedirectView.as_view(
                url='client/autotest.%(name)s/%(name)s.html'
                % dict(name=gwt_name))),
    ]

    return (pattern_list, debug_pattern_list)
