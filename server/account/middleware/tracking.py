from urllib.parse import unquote_plus, urlparse, parse_qs
from django.utils import timezone
from ..models import AccessLog


def make_ip_address_aware_request(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        request.ip_addr = x_forwarded_for.split(',')[0]
    else:
        request.ip_addr = request.META.get('REMOTE_ADDR')
    return request

    
def get_loggedin_user(request):
    if request.user.is_authenticated and not request.user.is_anonymous:
        return request.user 
    return None


class TrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = make_ip_address_aware_request(request)
        return self.get_response_with_writing_access_log(request)

    def get_response_with_writing_access_log(self, request):
        starts_at = timezone.now()
        response = self.get_response(request)
        latency = (timezone.now() - starts_at).microseconds / 1000

        try:
            status_code = getattr(response, 'status_code')
        except (AttributeError, ValueError, AssertionError):
            status_code = None

        try:
            comment = getattr(response, 'data').get('detail', '')
        except (AttributeError, ValueError, AssertionError):
            comment = ''

        requested_uri = request.get_full_path()
        
        access_log_data = {
            'ip_addr': request.ip_addr,
            'request_method': request.method,
            'requested_uri': unquote_plus(requested_uri.split('?', 1)[0]),
            'query_string': unquote_plus(urlparse(requested_uri).query),
            'status_code': status_code,
            'referer': request.META.get('HTTP_REFERER', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user': get_loggedin_user(request),
            'comment': comment,
            'latency': latency
        }
        AccessLog(**access_log_data).save()

        return response
