from ztg.models import RequestLog


class RequestLoggerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # skip logging for admin and static files
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)

        response = self.get_response(request)

        RequestLog.objects.create(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            ip_address=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        return response