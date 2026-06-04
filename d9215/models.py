from django.db import models
import uuid
from encrypted_model_fields import EncryptedEmailField

# Create your models here.
class audit_logs(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_name = models.CharField(max_length=255)
    record_id = models.UUIDField()
    user_id = models.UUIDField()
    action_taken = models.CharField(max_length=255)
    before_state = models.JSONField()
    after_state = models.JSONField()
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "d9215.audit_logs"
        managed = False

    def __str__(self):
        return f"Audit Log {self.log_id} - {self.action_taken} on {self.table_name}"
    

class rotary_focus_areas(models.Model):
    code = models.CharField(max_length=50, primary_key=True)
    label = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        db_table = "rotary_focus_areas"
        managed = False

    def __str__(self):
        return self.label
    
    
class districts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_number = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=200, null=False, blank=False)
    region = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "districts"
        managed = False

    def __str__(self):
        return f"District {self.district_number} - {self.name}"
    

class clubs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='clubs_dist')
    name = models.CharField(max_length=255, null=False, blank=False)
    email = EncryptedEmailField(unique=True, null=False)
    country = models.CharField(max_length=25, null=False, blank=False)  
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=False, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=8, null=False, blank=True)
    url_banner = models.URLField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100)
    zone_loc = models.CharField(max_length=100)
    charter_number = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, null=False)
    chatered_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "clubs"
        managed =  False 

    def __str__(self):
        return f"Club {self.name} - District {self.district_id.district_number}"
    

TENANT_TYPE_CHOICES = [
    ('club', 'Club'),
    ('district', 'District'),
    ('committee', 'Committee'),
]
ROLE_CHOICES = [
    ('club_president', 'Club President'),
    ('club_secretary', 'Club Secretary'),
    ('club_treasurer', 'Club Treasurer'),
    ('district_governor', 'District Governor'),
    ('district_secretary', 'District Secretary'),
    ('district_treasurer', 'District Treasurer'),
    ('district_pr','District PR'),
    ('drr','District Rotaract Representative'),
    ('adrr','Assistant District Rotaract Representative'),
    ('district_tech_lead', 'District Tech Lead'),
    ('club_pr', 'Club PR'),
]

class users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='users_club')
    tenant_type = models.CharField(max_length=20, choices=TENANT_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    email = EncryptedEmailField(unique=True, null=False)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=False)
    is_primary = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "users"
        managed = False 

    def __str__(self):
        return f"{self.name} - {self.role} at {self.club_id.name}"
    

class sessions(models.MOdel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user_id = models.ForeignKey(users, on_delete=moclaude the 4 council membersdels.PROTECT, related_name='user_sessions')
    token_hash  = models.CharField(max_length=255, unique=True, null=False)
    ip_address = models.IPAddressField()
    user_agent = models.CharField(max_length=500)
    expires_at = models.DateTimeField(null=False)
    revoked_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sessions"
        managed = False

    def __str__(self):
        return f"Session: {self.id} - {self.ip_address} - {self.user_agent}"
    

PERIOD_TYPE_CHOICES = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('semi_annually', 'Semi-Annually'),
    ('annually', 'Annually'),
]

class reporting_periods(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_rp_periods')
    label = models.CharField(max_length=100, null=False)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES, null=False)
    opens_at = models.DateTimeField(null=False)
    closes_at = models.DateTimeField(null=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        db_table = "d9215.reporting_periods"
        managed = False

    def __str__(self):
        return f"{self.label} - {self.district_id.name}"
    

class dockets_types(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_rp_dockets')
    code =  models.CharField(unique=True, max_length=50, null=False)
    name = models.CharField(max_length=100, null=False)
    description = models.TextField()
    schema_definition = models.JSONField(null=False)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "d9215.docket_types"
        managed = False

    def __str__(self):
        return f"Docket: {self.id} - {self.code} - {self.name}"


class reporting_dockets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_dockets')
    dockets_type_id = models.ForeignKey(dockets_types, on_delete=models.PROTECT, related_name='rps_per_docket')
    data = models.JSONField(null=False)
    

    class Meta:
        db_table = "d9215.reporting_dockets"
        managed = False


REPORT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("flagged", "Flagged for Review"),
    ("revision_request", "Revision Request"),
]

class club_reports(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_rps')
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_rps')
    reporting_period = models.ForeignKey(reporting_periods, on_delete=models.PROTECT, related_name='reports_rp_period')
    reporting_docket = models.ForeignKey(reporting_dockets, on_delete=models.PROTECT, related_name='club_docket_rps')

    status = models.CharField(max_length=25, choices=REPORT_STATUS_CHOICES, default="draft")
    version = models.IntegerField(default=1)
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models. PROTECT, related_name='rp_focus_area')

    submitted_at = models.DateTimeField(null=False, auto_now_add=True)
    submitted_by = models.ForeignKey(users, null=False, on_delete=models.SET_NULL, related_name='user_rp_submitted_by')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_rp_approved_by')

    flagged_at = models.DateTimeField(null=True, blank=True)
    flagged_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='user_rp_flagged_by')
    flagged_reason = models.TextField()

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='user_rp_reviewed_by')
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "d9215.club_reports"
        managed =  False

    def __str__(self):
        return f"Report {self.id} - {self.club_id.name} - {self.reporting_period_id.label}"
    

class reports_info(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_id = models.ForeignKey(club_reports, on_delete=models.PROTECT, related_name='rp_info')
    impact_metrics = models.JSONField(null=True, blank=True)
    featured_homepage = models.BooleanField(default=False)
    funds_raised = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rp_doc_link = models.URLField(max_length=255, null=False, blank=False)

    class Meta:
        db_table = "d9215.reports_info"
        managed =  False

    def __str__(self):
        return f"Report Info for {self.report_id.id}"


class report_comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_id = models.ForeignKey(club_reports, on_delete=models.PROTECT, related_name='rp_comments')
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_rp_comments')
    author_id = models.ForeignKey(users, on_delete=models.PROTECT, related_name='user_rp_comments')
    comment = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_comments_resolved_by')
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "d9215.report_comments"
        managed = False 

    def __str__(self):
        return f"Comment by {self.author_id.name} on Report {self.report_id.id}"
    

class event_types(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_event_types')
    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100, null=False)
    is_active = models.BooleanField(default=True, null=False)

    class Meta:
        db_table = "d9215.event_types"
        managed = False

    def __str__(self):
        return f"{self.label} - {self.code}"
    

EVENT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("pending_approval", "Pending Approval"),
    ("approved","Approved"),
    ("executed", "Executed"),
    ("cancelled", "Cancelled"),
]

class events(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_events')
    event_type_id = models.ForeignKey(event_types, on_delete=models.PROTECT, related_name='evnt_type')
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_event_type')
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models. PROTECT, related_name='event_focus_area')
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    planned_date = models.DateTimeField()
    actual_date = models.DateTimeField(null=True, blank=True)
    planned_start_time = models.TimeField()
    venue = models.CharField(max_length=255)
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(max_length=255, null=True, blank=True)
    attendees = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=EVENT_STATUS_CHOICES, default="draft")
    is_public = models.BooleanField(default=False)
    patner_clubs = models.ManyToManyField(clubs, related_name='event_partner_clubs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='event_created_by')  
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='event_approved_by')  
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "d9215.events"
        managed = False


    def __str__(self):
        return f"{self.title} - {self.club_id.name} - {self.event_date}"
    

BENEFICIARY_TYPE_CHOICES = [
    ("individuals", "Individuals"),
    ("communities", "Communities"),
    ("families", "Families"),
    ("schools", "Schools"),
    ("hospitals", "Hospitals"),
    ("organizations", "Organizations"),
    ("other", "Other"),
]

class projects(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_projects')
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='district_projects')
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models.PROTECT, related_name='project_focus_area')

    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField()
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=True, blank=True)

    beneficiary_type = models.CharField(max_length=50, choices=BENEFICIARY_TYPE_CHOICES, null=False, blank=False)
    budget_planned = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    actual_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    impact_metrics = models.JSONField(null=False)
    is_trf_funded = models.BooleanField(default=False, null=False)

    patner_organisations = models.JSONField()
    status = models.CharField(max_length=255, choices=EVENT_STATUS_CHOICES, default="draft")

    created_at = models.DateTimeField(auto_now_add=True)    
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_projects_created_by')  
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_projects_approved_by')  
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "d9215.projects"
        managed = False

    def __str__(self):
        return f"{self.title} - {self.club_id.name} - {self.start_date}"


ROLE_CHECK_TYPES = [
    ("launch","Launch"),
    ("execution","Execution"),
    ("monitoring","Monitoring"),
    ("closure","Closure"),
    ("fundraiser","Fundraiser"),
    ("awareness","Awareness")
]

class project_events(models.Model):
    project_id = models.ForeignKey(projects, on_delete=models.CASCADE, related_name='project_rel_event')
    event_id = models.ForeignKey(events, on_delete=models.CASCADE, related_name='event_rel_project')
    role = models.CharField(max_length=20, null=False, choices=ROLE_CHECK_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    

CONTENT_TYPE_CHOICES = [
    ("report", "Report"),
    ("event", "Event"),
    ("project", "Project"),
    ("story","Story")
]
FILE_TYPE_CHOICES = [
    ("image/JPEG", "Image"),
    ("image/PNG", "Image"),
    ("image/GIF", "Image"),
    ("application/pdf", "Document"),
    ("application/doc", "Document"),
    ("video/MP4", "Video"),
    ("other", "Other"),
]

class media_assets(models.Model):
    id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_media_assets')
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_media_assets')

    context_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    context_id = models.UUIDField(null=False, blank=False)
    storage_provider = models.CharField(max_length=30)
    storage_key = models.CharField(max_length=1000)
    public_url = models.URLField(max_length=100)

    file_type = models.CharField(max_length=255, choices=FILE_TYPE_CHOICES)
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    hash_code = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_media_aprroved_by')
    uploaded_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='user_media_uploaded_by')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "d9215.media_assets"
        managed = False

    def __str__(self):
        return f"Media {self.id} - {self.context_type} - {self.club_id.name}"


ACTIVITY_TYPE_CHOICES = [
    ("report_submitted", "Report Submitted"),
    ("report_approved", "Report Approved"),
    ("report_flagged", "Report Flagged"),
    ("event_created", "Event Created"),
    ("event_approved", "Event Approved"),
    ("event_executed", "Event Executed"),
    ("project_created", "Project Created"),
    ("project_approved", "Project Approved"),
    ("docket_submitted", "Docket Submitted"),
    ("story_submitted", "Story Submitted"),
    ("media_uploaded", "Media Uploaded"),
]

class club_activity_feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT, related_name='dist_activities')
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT, related_name='club_activities')
    actor_id = models.ForeignKey(users, on_delete=models.PROTECT, related_name='user_activities')
    activity_type = models.CharField(max_length=25, choices=ACTIVITY_TYPE_CHOICES)
    entity_type = models.CharField(max_length=255)
    entity_id = models.UUIDField()
    summary = models.CharField(max_length=500)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "d9215.club_activity_feed"
        managed = False

    def __str__(self):
        return f"Activity {self.activity_type} by {self.actor_id.name} at {self.created_at}"


class stories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)