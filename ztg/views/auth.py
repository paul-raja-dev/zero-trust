from ztg.services.jwt_service import generate_tokens, decode_token
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def login(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        # fallback to form data
        body = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }

    username = body.get('username')
    password = body.get('password')

    if not username or not password:
        return JsonResponse({'error': 'username and password are required'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user:
        tokens = generate_tokens(user)
        return JsonResponse({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'username': user.username,
            }
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)


@csrf_exempt
def refresh(request):
    """
    Validate a refresh token and issue a new access token.
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'invalid json body'}, status=400)

    refresh_token = body.get('refresh')

    if not refresh_token:
        return JsonResponse({'error': 'refresh token is required'}, status=400)

    # decode and verify the refresh token
    payload = decode_token(refresh_token)

    if not payload:
        return JsonResponse({'error': 'invalid or expired refresh token'}, status=401)

    # make sure it's actually a refresh token
    if payload.get('token_type') != 'refresh':
        return JsonResponse({'error': 'this is not a refresh token'}, status=401)

    # get the user and generate a new access token
    try:
        user = User.objects.get(id=payload['user_id'])
    except User.DoesNotExist:
        return JsonResponse({'error': 'user not found'}, status=404)

    tokens = generate_tokens(user)

    return JsonResponse({
        'access': tokens['access'],
        'message': 'token refreshed'
    })