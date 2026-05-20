import json
import jwt
import datetime
import uuid
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from .models import UserCredential, Session


def _hash_token_id(jti: str) -> str:
    # simple storage of jti as token_hash; could hash further if desired
    return str(jti)


@csrf_exempt
def login_issue_token(request: HttpRequest):
    """Simple token issuer for development/testing.

    Accepts JSON body with at least `user_id` and `role`. Optional: `zone`, `club`, `ip`, `current_district`.
    Returns a signed JWT using `settings.JWT_SECRET_KEY`.
    """
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    # For now we authenticate by user_id + password. This maps to public.users.id
    user_id = payload.get('user_id') or payload.get('sub')
    password = payload.get('password')
    if not user_id or not password:
        return JsonResponse({'detail': 'user_id and password are required'}, status=400)

    try:
        cred = UserCredential.objects.get(user_id=user_id)
    except UserCredential.DoesNotExist:
        return JsonResponse({'detail': 'invalid credentials'}, status=401)

    if not check_password(password, cred.password_hash):
        return JsonResponse({'detail': 'invalid credentials'}, status=401)

    now = datetime.datetime.utcnow()
    jti = str(uuid.uuid4())
    exp = now + datetime.timedelta(seconds=getattr(settings, 'JWT_EXP_DELTA_SECONDS', 3600))
    token_payload = {
        'sub': str(user_id),
        'role': payload.get('role') or cred.role if hasattr(cred, 'role') else payload.get('role'),
        'zone': payload.get('zone'),
        'club': payload.get('club') or payload.get('club_id') or payload.get('current_club_id'),
        'current_district': payload.get('current_district'),
        'iat': now,
        'exp': exp,
        'jti': jti
    }

    token = jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # store session revocation record in public.sessions
    try:
        Session.objects.create(
            user_id=user_id,
            token_hash=_hash_token_id(jti),
            ip_address=payload.get('ip') or request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            expires_at=exp,
        )
    except Exception:
        # don't fail login if session recording fails; log in production
        pass

    return JsonResponse({'access_token': token, 'token_type': 'bearer', 'expires_in': settings.JWT_EXP_DELTA_SECONDS})


def protected_test(request):
    payload = getattr(request, 'jwt_payload', None)
    if not payload:
        return JsonResponse({'detail': 'unauthenticated'}, status=401)
    return JsonResponse({'sub': payload.get('sub'), 'role': payload.get('role')})
