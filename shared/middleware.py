"""
pass the follwing details in rls middleware to be used for authentication
1. current_role: user table
2. current_club_id : user table 
3. current_zone : district table (joined via: district -district_id-> club -club_id-> user)
4. current_user_id : user table 
"""

from django.db import connection, transaction


class RLSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        with transaction.atomic():
            self._set_rls_vars(request)
            return self.get_response(request)

    def _set_rls_vars(self, request):
        user = request.user
        zone = self._resolve_zone(user)

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT
                    set_config('district9215.current_user_id', %s, true),
                    set_config('district9215.current_club_id', %s, true),
                    set_config('district9215.current_zone', %s, true),
                    set_config('district9215.current_role', %s, true)
                """,
                [
                    str(user.user_id) if user.user_id  is not None else "",
                    str(user.club_id) if user.club_id  is not None else "",
                    str(zone) if zone is not None else "",
                    str(user.role) if user.role is not None else "",
                ],
            )

    @staticmethod
    def _resolve_zone(user) -> str | None:
        if hasattr(user, "_cached_zone"):
            return user._cached_zone

        with connection.cursor() as cur:
            cur.execute(
                """
                SELECT d.zone FROM district d JOIN club c ON c.district_id = d.district_id
                WHERE  c.club_id = %s
                LIMIT  1
                """,
                [str(user.club_id)],
            )
            row = cur.fetchone()

        zone = row[0] if row else None
        user._cached_zone = zone         
        return zone