from django.http import JsonResponse
import time

class RateLimiter:

    request_counts= {}
    rate_limit = 5    # max request in given window_size
    window_size = 10  # number of seconds to refresh the request count

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        

        ip_addr = request.META.get('REMOTE_ADDR')

        lst_time_stamp = self.request_counts.get(ip_addr,[])
        lst_time_stamp.append(time.time())

        filtered_list =[]
        current_time = time.time()
        

        for tim in lst_time_stamp:
            if tim > current_time - self.window_size:
                filtered_list.append(tim)


        self.request_counts[ip_addr] = filtered_list

        if len(filtered_list) > self.rate_limit:
            return JsonResponse({'error' : 'Too many request'},status = 429)

        print(self.request_counts)


        
        response = self.get_response(request)

        return response