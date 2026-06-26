from django.http import JsonResponse
from ztg.services.jwt_service import decode_token


class JWTAuthenticationMiddleware:

    exempt_paths = [
        '/admin/login',
        '/api/login/',
        '/api/register',
    ]

    def __init__(self,get_response):
        self.get_response = get_response
    
    def __call__(self, request):

        for path in self.exempt_paths:
            if request.path.startswith(path):
                return self.get_response(request)
        
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            try :
                head,token = auth_header.split()
            except ValueError:
                return JsonResponse({'msg':'Invaild authorization header'},status = 401)

            if head=='Bearer':
                result = decode_token(token)
                if result:
                    request.user = result
                else:
                    return JsonResponse({'msg':'token expired'},status = 401)

            else:
                return JsonResponse({'msg':'unauthorized access'},status = 401)
        else:
            return JsonResponse({'msg': 'Authorization token is required'}, status=401)


        response = self.get_response(request)


        return response
        