"""
this file contains the raw sql statements that will be mapped to the querries file
"""

# audit logs sql 
AUDIT_LOGS_SQL = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs 
    GROUP BY table_name, ip_address 
    ORDER BY created_at DESC;
"""

AUDIT_LOGS_BTWN_PERIODS_SQL = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs
    WHERE created_date BETWEEN %s AND %s 
    GROUP BY table_name, ip_address 
    ORDER BY created_at DESC;
"""

AUDIT_LOGS_USER_SQL = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs
    WHERE user_id = %s 
    GROUP BY table_name, ip_address
    ORDER BY created_at DESC;
"""

# clubs sql 
CLUB_VIEW_SQL = """
    SELECT district.name, club.name, club.email, club.country, club.region, club.zone_loc, club.charter_number, club.is_ative, club.chartered_at FROM clubs AS club
    INNER JOIN districts AS district ON club.district_id = district.id
    WHERE club.is_active = TRUE, deleted_at = NULL
    GROUP BY district.name, club.zone_loc, club.country
    ORDER BY club.name, club.chartered_at DESC;
"""

CLUB_ADD_SQL = """
    INSERT INTO clubs (id, district_id, name, email, country, latitude, longitude, url_banner, region, zone_loc, charter_number, is_active, chartered_at, created_at)
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
    RETURNING id;
"""

CLUB_EDIT_SQL = """
    UPDATE clubs SET name = COALESCE(%s, name), email = COALESCE(%s, email), zone_loc = COALESCE(%s, zone_loc), url_banner = COALESCE(%s, url_banner), is_active = COALESCE(%s, is_active)
    WHERE id = %s AND district_id = %s AND deleted_at IS NULL
    RETURNING id;
"""
CLUB_ADRR_EDIT_SQL = """

"""

CLUB_DELETE_SQL = """
    UPDATE clubs SET deleted_at = now() 
    WHERE id = %s AND district_id = %s AND deleted_at IS NULL 
    RETURNING id;
"""

# users sql 
USERS_VIEW_SQL = """
    SELECT id, tenant_type, club_id, role, zone_loc, is_primary, assigned_at, revoked_at
    FROM users
    WHERE revoked_at IS NULL
    GROUP BY role, tenant_type
    ORDER BY club_id;
"""

USER_ADRR_VIEW_SQL = """
    SELECT u.id, u.role, u.club_id, u.zone_loc, u.revoked_at FROM users u
    INNER JOIN clubs c ON c.id = u.club_id
    WHERE c.zone_loc = current_setting('district9215.current_zone') AND u.revoked_at IS NULL
    GROUP BY role, tenant_type
    ORDER BY club_id;
"""

USERS_ADD_SQL = """
    INSERT INTO users (id, tenant_type, club_id, role, zone_loc, is_primary, assigned_at, assigned_by, revoked_at) 
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, NOW(), %s, NULL)
    RETURNING id;
"""

USERS_DRR_DELETE_SQL = """
    UPDATE users SET revoked_at = NOW()
    WHERE id = %s AND revoked_at IS NULL;
"""

USER_ADRR_DELETE_SQL = """
    UPDATE users user SET user.revoked_at = NOW() 
    FROM clubs club
    WHERE user.id = %s AND revoked_at IS NULL AND user.club_id = club.id
    AND club.zone_loc = current_setting('district9215.current_zone', TRUE);
"""


USERS_ADRR_UPDATE_SQL = """
    UPDATE users user SET user.tenant_type = COALESCE(%s, tenant_type), user.role = COALESCE(%s, role), user.is_primary = COALESCE(%s, is_primary), name = COALESCE(%s, name), email = COALESCE(%s, email)  
    FROM clubs club
    WHERE user.id = %s AND revoked_at IS NULL AND user.club_id = club.id
    AND club.zone_loc = current_setting('district9215.current_zone', TRUE);
"""

USERS_ADRR_UPDATE_SQL = """
    UPDATE users user SET user.tenant_type = COALESCE(%s, tenant_type), user.role = COALESCE(%s, role), user.is_primary = COALESCE(%s, is_primary), name = COALESCE(%s, name), email = COALESCE(%s, email)  
    FROM clubs club
    WHERE user.id = %s AND revoked_at IS NULL AND user.club_id = club.id
    AND club.district_id = %s;
"""

# VALID_ROLES = {
#     'club_president','club_treasurer','club_secretary','club_pr',
#     'adrr','district_pr','district_treasurer','drr','district_tech_lead'
# }

CHANGE_ROLE_SQL  = """
    UPDATE users SET role = %s, assigned_at = NOW(), assigned_by = %s
    WHERE id = %s AND revoked_at IS NULL;
"""

# reporting periods 
INSERT_RP_PERIOD = """
    INSERT INTO d9215.reporting_periods (id, district_id, label, period_type, opens_at, closes_at, is_locked, created_by)
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, label, opens_at, closes_at, is_locked;
"""

VIEW_RP_PERIODS = """
    SELECT id, label, period_type, opens_at, closes_at, is_locked, created_at
    FROM d9215.reporting_periods
    WHERE district_id = %s AND is_locked = %s
    ORDER BY opens_at DESC;
"""

VIEW_OPEN_RP_PERIOD = """
    SELECT id, label, period_type, opens_at, closes_at
    FROM d9215.reporting_periods
    WHERE district_id = %s AND period_type = %s AND is_locked = FALSE
    AND opens_at <= NOW() AND closes_at >= NOW();
"""

LOCK_RP_PERIOD = """
    UPDATE d9215.reporting_periods SET is_locked = TRUE
    WHERE id = %s AND district_id = %s AND is_locked = FALSE
    RETURNING id, label, is_locked;
"""

UNLOCK_RP_PERIOD = """
    UPDATE d9215.reporting_periods SET is_locked = FALSE
    WHERE id = %s AND district_id = %s AND is_locked = TRUE
    RETURNING id, label, is_locked;
"""

# club reports 
INSERT_CLUB_REPORT = """
    INSERT INTO d9215.club_reports (id, district_id, club_id, reporting_period, report_docket, status, version, focus_area, submitted_by, created_at)
    SELECT gen_random_uuid(), %s, %s, %s, %s, 'draft', 1, %s, %s, now()
    FROM d9215.reporting_periods rp
    WHERE rp.id = %s AND rp.opens_at <= now() AND rp.closes_at >= now() AND rp.is_locked = false
    RETURNING id, status, version, created_at;
"""

VIEW_CLUB_REPORT = """
    SELECT id, club_id, reporting_period, status, version, focus_area, submitted_at, approved_at, deleted_at
    FROM d9215.club_reports
    WHERE club_id = %s AND deleted_at IS NULL AND (%s::uuid IS NULL OR reporting_period = %s)
    ORDER BY created_at DESC;
"""

VIEW_ADRR_CLUB_REPORT = """
    SELECT cr.id, cr.club_id, c.zone_loc, cr.status, cr.submitted_at, cr.flagged_reason
    FROM d9215.club_reports cr
    JOIN public.clubs c ON c.id = cr.club_id
    WHERE c.zone_loc = %s AND cr.reporting_period = %s AND cr.deleted_at IS NULL
    ORDER BY cr.submitted_at DESC NULLS LAST;
"""