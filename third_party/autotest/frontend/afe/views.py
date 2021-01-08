import httplib2, os, sys, traceback, cgi

from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.http import HttpResponseServerError
from django.template import Context, loader
from client.common_lib import utils
from frontend import views_common
from frontend.afe import models, rpc_handler, rpc_interface
from frontend.afe import rpc_utils

moblab_rpc_interface = utils.import_site_module(
        __file__, 'frontend.afe.moblab_rpc_interface',
        dummy=object())

# since moblab_rpc_interface is later in the list, its methods will
# override those of rpc_interface
rpc_handler_obj = rpc_handler.RpcHandler((rpc_interface,
                                          moblab_rpc_interface),
                                         document_module=rpc_interface)


def handle_rpc(request):
    """Handle the RPC request.

    @param request: the RPC request.
    """
    return rpc_handler_obj.handle_rpc_request(request)


def rpc_documentation(request):
    """Return the rpc documentation.

    @param request: the RPC request.
    """
    return rpc_handler_obj.get_rpc_documentation()


def redirect_with_extra_data(request, url, **kwargs):
    """Redirect according to the extra data.

    @param request: the RPC request.
    @param url: the partial redirected url.
    @param kwargs: the parameters used in redirection.
    """
    kwargs['getdata'] = request.GET.urlencode()
    kwargs['server_name'] = request.META['SERVER_NAME']
    return HttpResponsePermanentRedirect(url % kwargs)


GWT_SERVER = 'http://localhost:8888/'
def gwt_forward(request, forward_addr):
    """Get the response from forwarding address.

    @param request: the RPC request.
    @param forward_addr: the forwarding address.
    """
    url = GWT_SERVER + forward_addr
    if len(request.POST) == 0:
        headers, content = httplib2.Http().request(url, 'GET')
    else:
        headers, content = httplib2.Http().request(url, 'POST',
                                                   body=request.body)
    http_response = HttpResponse(content)
    for header, value in headers.iteritems():
        if header not in ('connection',):
            http_response[header] = value
    return http_response


def handler500(request):
    """Redirect to error website page.

    @param request: the RPC request.
    """
    t = loader.get_template('500.html')
    trace = traceback.format_exc()
    context = {
        'type': sys.exc_info(),
        'value': sys.exc_info(),
        'traceback': cgi.escape(trace)
    }
    return HttpResponseServerError(t.render(context))


def handle_file_upload(request):
    """Handler for uploading files.

    Saves the files to /tmp and returns the resulting paths on disk.

    @param request: request containing the file data.

    @returns HttpResponse: with the paths of the saved files.
    """
    if request.method == 'POST':
        TEMPT_DIR = '/tmp/'
        file_paths = []
        for file_name, upload_file in request.FILES.iteritems():
            file_path = os.path.join(
                    TEMPT_DIR, '_'.join([file_name, upload_file.name]))
            with open(file_path, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)
            file_paths.append(file_path)
        return HttpResponse(rpc_utils.prepare_for_serialization(file_paths))
