from django.http import JsonResponse

class RateLimiter:

    request_counts= {}

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        

        ip_addr = request.META.get('REMOTE_ADDR')

        self.request_counts[ip_addr] = self.request_counts.get(ip_addr,0) + 1

        print(self.request_counts)

        if self.request_counts[ip_addr]>5:
            return JsonResponse({'error' : 'too many request'},status = 429)
        
        response = self.get_response(request)

        return response