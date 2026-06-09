"""
this file contains the raw sql statements that will be mapped to the querries file
"""

# audit logs sql 
AUDIT_LOGS = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs 
    GROUP BY table_name, ip_address 
    ORDER BY created_at DESC;
"""

AUDIT_LOGS_BTWN_PERIODS = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs
    WHERE created_date BETWEEN %s AND %s 
    GROUP BY table_name, ip_address 
    ORDER BY created_at DESC;
"""

AUDIT_LOGS_USER = """
    SELECT table_name, record_id, user_id, action_taken, before_state, after_state, ip_address, created_at FROM d9215.audit_logs
    WHERE user_id = %s 
    GROUP BY table_name, ip_address
    ORDER BY created_at DESC;
"""

# clubs sql 
CLUB_VIEW = """
    SELECT district.name, club.name, club.email, club.country, club.region, club.zone_loc, club.charter_number, club.is_ative, club.chartered_at FROM clubs AS club
    INNER JOIN districts AS district ON club.district_id = district.id
    WHERE club.is_active = TRUE, deleted_at = NULL
    GROUP BY district.name, club.zone_loc, club.country
    ORDER BY club.name, club.chartered_at DESC;
"""

CLUB_ADD = """
    INSERT INTO clubs (id, district_id, name, email, country, latitude, longitude, url_banner, region, zone_loc, charter_number, is_active, chartered_at, created_at)
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
    RETURNING id;
"""

CLUB_EDIT = """
    UPDATE clubs SET name = COALESCE(%s, name), email = COALESCE(%s, email), zone_loc = COALESCE(%s, zone_loc), url_banner = COALESCE(%s, url_banner), is_active = COALESCE(%s, is_active)
    WHERE id = %s AND district_id = %s AND deleted_at IS NULL
    RETURNING id;
"""
CLUB_ADRR_EDIT = """

"""

CLUB_DELETE = """
    UPDATE clubs SET deleted_at = now() 
    WHERE id = %s AND district_id = %s AND deleted_at IS NULL 
    RETURNING id;
"""

# users sql 
USERS_VIEW = """
    SELECT id, tenant_type, club_id, role, zone_loc, is_primary, assigned_at, revoked_at
    FROM users
    WHERE revoked_at IS NULL
    GROUP BY role, tenant_type
    ORDER BY club_id;
"""

USER_ADRR_VIEW = """
    SELECT u.id, u.role, u.club_id, u.zone_loc, u.revoked_at FROM users u
    INNER JOIN clubs c ON c.id = u.club_id
    WHERE c.zone_loc = current_setting('district9215.current_zone') AND u.revoked_at IS NULL
    GROUP BY role, tenant_type
    ORDER BY club_id;
"""

USERS_ADD = """
    INSERT INTO users (id, tenant_type, club_id, role, zone_loc, is_primary, assigned_at, assigned_by, revoked_at) 
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, NOW(), %s, NULL)
    RETURNING id;
"""

USERS_DRR_DELETE = """
    UPDATE users SET revoked_at = NOW()
    WHERE id = %s AND revoked_at IS NULL;
"""

USER_ADRR_DELETE = """
    UPDATE users user SET user.revoked_at = NOW() 
    FROM clubs club
    WHERE user.id = %s AND revoked_at IS NULL AND user.club_id = club.id
    AND club.zone_loc = current_setting('district9215.current_zone', TRUE);
"""


USERS_ADRR_UPDATE = """
    UPDATE users user SET user.tenant_type = COALESCE(%s, tenant_type), user.role = COALESCE(%s, role), user.is_primary = COALESCE(%s, is_primary), name = COALESCE(%s, name), email = COALESCE(%s, email)  
    FROM clubs club
    WHERE user.id = %s AND revoked_at IS NULL AND user.club_id = club.id
    AND club.zone_loc = current_setting('district9215.current_zone', TRUE);
"""

USERS_ADRR_UPDATE = """
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

# report dockets 
INSERT_RP_DOCKET = """
    INSERT INTO d9215.report_dockets (id, docket_type_id, data, submitted_by, submitted_at, created_at, updated_at)
    VALUES (gen_random_uuid(), %s, %s::jsonb, %s, NOW(), NOW(), NOW())
    ON CONFLICT (docket_type_id) DO NOTHING
    RETURNING id, docket_type_id, submitted_at;
"""

VIEW_RP_DOCKET = """
    SELECT id, docket_type_id, data, submitted_by, submitted_at, created_at, updated_at
    FROM d9215.report_dockets
    WHERE id = %s;
"""

UPDATE_RP_DOCKET = """
    UPDATE d9215.report_dockets SET data = %s::jsonb, submitted_by = %s, submitted_at = NOW(), updated_at   = NOW()
    WHERE id = %s 
    RETURNING id, updated_at;
"""

DELETE_RP_DOCKET = """
    DELETE FROM d9215.report_dockets
    WHERE id = %s
    RETURNING id;
"""

# report comments 
INSERT_RP_COMMENT = """
    INSERT INTO d9215.report_comments (id, report_id, club_id, author_id, comment, is_read, created_at)
    VALUES (%s, %s, %s, %s, %s, FALSE, NOW())
    RETURNING author_id, created_at;
"""

VIEW_CLUB_RP_COMMENT = """
    SELECT id, report_id, club_id, author_id, comment, is_read, created_at, resolved_by, resolved_at
    FROM d9215.report_comments
    WHERE report_id = %s
    ORDER BY created_at ASC'
"""

VIEW_ADRR_RP_COMMENT = """
    SELECT rc.id, rc.report_id, rc.club_id, rc.author_id, rc.comment, rc.is_read, rc.created_at
    FROM d9215.report_comments rc
    INNER JOIN d9215.club_reports cr ON cr.id = rc.report_id
    INNER JOIN public.clubs c ON c.id  = rc.club_id
    WHERE rc.resolved_at IS NULL AND c.zone_loc = %s    
    ORDER BY rc.created_at ASC;
"""

UPDATE_RP_COMMENT = """
    UPDATE d9215.report_comments SET resolved_by = %s, resolved_at = NOW(), is_read = TRUE
    WHERE id = %s
    AND resolved_at IS NULL;
"""

# events sql 
INSERT_EVENT = """
    INSERT INTO d9215.events ( id, district_id, club_id, event_type_id, focus_area, title, description, planned_date, venue, is_virtual, is_public, status, created_by, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, NOW(), NOW()) 
    RETURNING id, status, created_at;
"""

VIEW_EVENTS = """
    SELECT id, title, status, planned_date, actual_date, is_virtual, venue, attendees, is_public
    FROM d9215.events
    WHERE club_id = %s AND deleted_at IS NULL
    ORDER BY planned_date DESC;
"""

VIEW_ADRR_EVENT = """
    SELECT e.id, e.title, e.status, e.planned_date, c.name AS club_name
    FROM d9215.events e
    JOIN public.clubs c ON c.id = e.club_id
    WHERE c.zone_loc = %s
    AND e.district_id = %s AND e.deleted_at IS NULL
    ORDER BY e.planned_date DESC;
"""

VIEW_PUBLIC_EVENTS = """
    SELECT id, title, planned_date, venue, is_virtual, focus_area
    FROM d9215.events
    WHERE district_id = %s
    AND is_public = TRUE AND status IN ('approved', 'executed') AND deleted_at IS NULL;
"""

# projects
INSERT_PROJECT = """
    INSERT INTO d9215.projects (id, district_id, club_id, focus_area, title, description, start_date, end_date,
        beneficiary_type, budget_planned, budget_currency, impact_metrics, partner_organisations, is_trf_funded, linked_report_period, status, created_by) 
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, 'planning', %s) 
    RETURNING id, created_at;
"""

SELECT_PROJECT = """
    SELECT id, club_id, focus_area, title, status, budget_planned, budget_actual, budget_currency, start_date, end_date, deleted_at
    FROM d9215.projects
    WHERE title = %s AND deleted_at IS NULL;
"""

SELECT_PROJECTS_BY_ZONE = """
    SELECT p.*
    FROM d9215.projects p
    JOIN public.clubs c ON c.id = p.club_id
    WHERE p.deleted_at IS NULL AND p.district_id = %s
    AND c.zone_loc = %s      
    ORDER BY p.created_at DESC;
"""

UPDATE_PROJECT = """
    UPDATE d9215.projects
    SET title = COALESCE(%s, title), status = COALESCE(%s, status), budget_actual = COALESCE(%s, budget_actual), 
    impact_metrics = COALESCE(%s::jsonb, impact_metrics), updated_at = now()
    WHERE id = %s AND club_id = %s AND deleted_at IS NULL
    RETURNING id, status, updated_at;
"""

# stories 
INSERT_STORY = """
    INSERT INTO d9215.stories (id, district_id, club_id, event_id, project_id, title, body, excerpt, author_name, 
    author_user_id, content_type, status, approved_for_website, approved_for_newsletter, approved_for_magazine, slug, created_at, updated_at) 
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', false, false, false, %s, NOW(), NOW())
    RETURNING id, slug, status;
"""

VIEW_STORY = """
    SELECT id, club_id, title, excerpt, content_type, status, approved_for_website, approved_for_newsletter, approved_for_magazine, slug, published_at, created_at
    FROM d9215.stories
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC;
"""

PUBLIC_VIEW_STORIES = """"
    SELECT id, title, excerpt, author_name, slug, published_at
    FROM d9215.stories
    WHERE status = 'published'
    AND deleted_at IS NULL
    ORDER BY published_at DESC;
"""

APPROVE_STORY = """
    UPDATE d9215.stories SET status = %s, approved_by = %s, approved_at = NOW(), approved_for_website = %s, approved_for_newsletter = %s, 
    approved_for_magazine = %s, revision_notes = %s, updated_at = NOW()
    WHERE id = %s AND deleted_at IS NULL
    RETURNING id, status;
"""

CLUB_STORY_EDIT = """
    UPDATE d9215.stories SET title = %s, body = %s, excerpt = %s, content_type = %s, updated_at = NOW()
    WHERE id = %s AND status IN ('draft', 'pending_review', 'revision_requested') AND deleted_at IS NULL
    RETURNING id, updated_at;
"""

# MEDIA ASSETS SQL 
INSERT_MEDIA = """
    INSERT INTO d9215.media_assets (id, district_id, club_id, context_type, context_id, storage_provider, storage_key, public_url, file_type,
    file_size_bytes, width, height, duration_seconds, alt_text, original_filename, hash_code, is_approved, uploaded_by) 
    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, false, %s)
    RETURNING id, public_url, created_at;
"""

CLUB_VIEW_MEDIA = """
    SELECT * FROM d9215.media_assets
    WHERE club_id = current_setting('district9215.current_club_id')::uuid;
"""

ADRR_VIEW_MEDIA = """
    SELECT ma.* FROM d9215.media_assets ma
    JOIN public.clubs c ON c.id = ma.club_id
    WHERE c.zone_loc = current_setting('district9215.current_zone');
"""

DRR_VIEW_MEDIA = """
    SELECT * FROM d9215.media_assets;
"""

PUBLIC_VIEW_MEDIA = """
    SELECT id, public_url, alt_text, file_type, context_type, context_id
    FROM d9215.media_assets
    WHERE is_approved = true;
"""

APPROVE_MEDIA = """
    UPDATE d9215.media_assets SET is_approved = true, approved_by = %s
    WHERE id = %s AND is_approved = false
    RETURNING id, is_approved;
"""

DELETE_MEDIA = """
    DELETE FROM d9215.media_assets
    WHERE id = %s AND club_id = current_setting('district9215.current_club_id')::uuid;
"""

# ACTIVITY FEED 
INSERT_ACTIVITY_FEED = """
    INSERT INTO d9215.club_activity_feed (id, district_id, club_id, actor_id, activity_type, entity_type, entity_id, summary, metadata, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
    """

CLUB_VIEW_ACTIVITY_FEED = sql = """
    SELECT id, activity_type, entity_type, entity_id, summary, metadata, created_at
    FROM d9215.club_activity_feed
    WHERE club_id = %s
    ORDER BY created_at DESC
    LIMIT %s;
    """

ADRR_VIEW_ACTIVITY_FEED = base = """
    SELECT f.id, f.club_id, f.actor_id, f.activity_type, f.entity_type, f.entity_id, f.summary, f.created_at
    FROM d9215.club_activity_feed f
    JOIN public.clubs c ON c.id = f.club_id
    WHERE c.zone_loc = %s      
    """

DRR_VIEW_ACTIVITY_FEED = """
    SELECT id, activity_type, entity_type, entity_id, summary, metadata, created_at
    FROM d9215.club_activity_feed
    ORDER BY created_at DESC
    LIMIT %s;
"""
