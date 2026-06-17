import jwt
from datetime import datetime,timedelta,timezone
from django.conf import settings

def generate_tokens(user):

    now = datetime.now(timezone.utc)

    access_payload = {
            'user_id' : user.id,
            'token_type' : 'access',
            'exp' : now + timedelta(minutes=15),
            'iat' : now
            
    }

    refresh_payload = {
            'user_id' : user.id,
            'token_type' : 'refresh',
            'exp' : now+timedelta(days=7),
            'iat' : now
    }

    return {
        'access' : jwt.encode(access_payload,settings.SECRET_KEY,algorithm='HS256'),
        'refersh' : jwt.encode(refresh_payload,settings.SECRET_KEY,algorithm='HS256')
    }


def decode_token(token):

    try:
        return jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
    except (jwt.ExpiredSignatureError,jwt.InvalidTokenError):
        return None