from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from django.conf import settings
from types import SimpleNamespace
from .models import Session


class JWTAuthentication(BaseAuthentication):
    """DRF authentication class validating JWT and revocation via `public.sessions`.
    Returns a lightweight user object with `.id` and `.role`.
    """
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()

        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('token_expired')
        except Exception:
            raise exceptions.AuthenticationFailed('invalid_token')

        jti = payload.get('jti')
        if jti:
            s = Session.objects.filter(token_hash=str(jti)).first()
            if not s or s.revoked_at is not None:
                raise exceptions.AuthenticationFailed('token_revoked')

        user_id = payload.get('sub')
        if not user_id:
            raise exceptions.AuthenticationFailed('invalid_token')

        user = SimpleNamespace()
        user.id = user_id
        user.role = payload.get('role')
        user.is_authenticated = True

        # provide payload for downstream code
        request.jwt_payload = payload

        return (user, token)
