from django.http import JsonResponse

class IPBlockerMiddleware:

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):

        blocked_ips = []

        if request.META.get('REMOTE_ADDR') in blocked_ips:
            return JsonResponse({'error':'access denied'},status=403)
        
        response=self.get_response(request)

        return response
                 
        