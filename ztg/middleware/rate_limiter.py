from django.http import JsonResponse
import time

class RateLimiter:

    request_counts= {}

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        

        ip_addr = request.META.get('REMOTE_ADDR')

        lst_time_stamp = self.request_counts.get(ip_addr,[])
        lst_time_stamp.append(time.time())

        self.request_counts[ip_addr] = lst_time_stamp

        print(self.request_counts)


        
        response = self.get_response(request)

        return response