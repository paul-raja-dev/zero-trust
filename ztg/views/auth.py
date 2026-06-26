from ztg.services.jwt_service import generate_tokens
from django.http import JsonResponse
from django.contrib.auth import authenticate


def login(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},status=405)

    # 1. Read username/password from request
    # 2. Validate credentials
    # 3. Generate JWT tokens
    # 4. Return tokens as JSON
    
    user = authenticate(request,
                        username = request.POST.get("username"),
                        password = request.POST.get("password"))
    
    if user:
        tokens = generate_tokens(user)
        return JsonResponse({'access':tokens['access'],
                             'refresh':tokens['refresh']})
    else:
        return JsonResponse({'msg':'Invalid credentials'},status = 401)






def refresh(request):
    """
    Validate a refresh token and
    issue a new access token.
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    # 1. Read refresh token
    # 2. Decode and verify it
    # 3. Ensure token_type == "refresh"
    # 4. Generate a new access token
    # 5. Return the new access token

    return JsonResponse(
        {
            "message": "Refresh endpoint"
        },
        status=200
    )