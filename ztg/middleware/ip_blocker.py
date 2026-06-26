from django.http import JsonResponse
from ztg.models import BlockedIP, ThreatEvent


class IPBlockerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.path.startswith('/admin') or request.path.startswith('/static'):
            return self.get_response(request)

        client_ip = request.META.get('REMOTE_ADDR')

        blocked = BlockedIP.objects.filter(ip_address=client_ip, is_active=True).first()

        if blocked:
            # log this as a threat event
            ThreatEvent.objects.create(
                threat_type='blocked_access',
                severity='medium',
                ip_address=client_ip,
                description=f'Blocked IP tried to access {request.path}. Reason: {blocked.reason}'
            )
            return JsonResponse({'error': 'access denied'}, status=403)

        response = self.get_response(request)
        return response