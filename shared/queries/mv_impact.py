from typing import Optional
from shared.middleware import RLSMiddleware
from django.db import connection

def refresh_mv_impact() -> None:
     with connection.cursor() as cur:
        cur.execute(
            "REFRESH MATERIALIZED VIEW CONCURRENTLY d9215.mv_district_impact"
        )

def fetch_impact(dist_no: str, month: Optional[str] = None, focus_area: Optional[str] = None) -> list[dict]:
    refresh_mv_impact()
    filters = ["district_number = %s"]
    params = [dist_no]

    if month:
        filters.append("month = %s")
        params.append(month)
    if focus_area:
        filters.append("focus_area = %s")
        params.append(focus_area)

    where = " AND ".join(filters)

    sql = f"""
        SELECT district_number, month, projects_total, projects_completed, beneficiaries_total, spend_total, focus_area, refreshed_at
        FROM d9215.mv_district_impact
        WHERE {where}
        ORDER BY month DESC, focus_area
    """
    with connection.cursor() as cur:
        cur.execute(sql, params)
        cols = [c.description[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    

