import json
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
from django.http import HttpRequest
import jwt
from d9215.models import Session


class JWTAuthMiddleware(MiddlewareMixin):
    """Middleware that decodes a JWT from the Authorization header and
    sets PostgreSQL session settings used by the database RLS policies.

    Expected token claims (recommended):
      - sub or user_id: uuid of the user
      - role: current role string
      - zone: current zone
      - club: current club id
      - ip: optional client ip
    """

    def _is_postgres(self):
        engine = settings.DATABASES.get('default', {}).get('ENGINE', '')
        return 'postgresql' in engine or 'psycopg2' in engine

    def process_request(self, request: HttpRequest):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()

        payload = None
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            except Exception:
                payload = None

        request.jwt_payload = payload

        if payload:
            request.current_role = payload.get('role') or payload.get('current_role')
            request.current_zone = payload.get('zone') or payload.get('current_zone')
            request.current_club_id = payload.get('club') or payload.get('current_club_id')
            request.user_id = payload.get('sub') or payload.get('user_id')

        if self._is_postgres() and payload:
            claim_map = getattr(settings, 'DISTRICT9215_JWT_CLAIMS', {})
            with connection.cursor() as cur:
                for claim_key, setting_name in claim_map.items():
                    val = None
                    if claim_key == 'user_id':
                        val = payload.get('sub') or payload.get('user_id')
                    elif claim_key == 'user_ip':
                        val = payload.get('ip') or request.META.get('REMOTE_ADDR')
                    else:
                        val = payload.get(claim_key)

                    if val is None:
                        continue

                    try:
                        cur.execute("SET LOCAL %s = %s" % (setting_name, '%s'), [str(val)])
                    except Exception:
                        pass

        if payload:
            jti = payload.get('jti')
            if jti:
                try:
                    s = Session.objects.filter(token_hash=str(jti)).first()
                    if not s or s.revoked_at is not None:
                        request.jwt_payload = None
                except Exception:
                    pass
