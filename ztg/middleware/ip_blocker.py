from django.http import JsonResponse
from ztg.models import BlockedIP

class IPBlockerMiddleware:

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):

        client_ip = request.META.get('REMOTE_ADDR')

        is_blocked = BlockedIP.objects.filter(ip_address=client_ip,is_active=True).exists()

        if is_blocked:
            return JsonResponse({'error':'access denied'},status=403)
        
        response=self.get_response(request)

        return response
                 
        