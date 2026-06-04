from django.db import models
import uuid
from datetime import timedelta, datetime
from encrypted_model_fields import EncryptedCharField, EncryptedTextField, EncryptedEmailField, EncryptedDateTimeField

# Create your models here.
class audit_logs(models.Model):
    log_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table_name = models.CharField(max_length=255)
    record_id = models.UUIDField()
    user_id = models.UUIDField()
    action_taken = models.CharField(max_length=255)
    before_state = EncryptedTextField()
    after_state = EncryptedTextField()
    ip_address = models.GenericIPAddressField()
    timestamp = EncryptedDateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit Log {self.log_id} - {self.action_taken} on {self.table_name}"
    

class rotary_focus_areas(models.Model):
    code = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label
    
    
class districts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_number = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"District {self.district_number} - {self.name}"
    
    
class clubs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    email = EncryptedEmailField()
    country = models.CharField(max_length=255)  
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    url_banner = models.URLField(max_length=500, null=True, blank=True)
    region = models.CharField(max_length=255)
    zone_loc = models.CharField(max_length=255)
    charter_number = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    chatered_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

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
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    tenant_type = models.CharField(max_length=20, choices=TENANT_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    email = EncryptedEmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    zone_loc = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.role} at {self.club_id.name}"
    
PERIOD_TYPE_CHOICES = [
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('semi_annually', 'Semi-Annually'),
    ('annually', 'Annually'),
]


class reporting_periods(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    label = models.CharField(max_length=255)
    period_type = models.CharField(max_length=255, choices=PERIOD_TYPE_CHOICES)
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.label} - {self.district_id.name}"
    
REPORT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("submitted", "Submitted"),
    ("approved", "Approved"),
    ("flagged", "Flagged for Review"),
    ("revision_request", "Revision Request"),
]


class club_reports(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    reporting_period_id = models.ForeignKey(reporting_periods, on_delete=models.PROTECT)
    status = models.CharField(max_length=255, choices=REPORT_STATUS_CHOICES, default="draft")
    version = models.IntegerField(default=1)
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models. PROTECT)
    report_data = EncryptedTextField()
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='submitted_reports')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_reports')
    flagged_at = models.DateTimeField(null=True, blank=True)
    flagged_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='flagged_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.PROTECT, related_name='reviewed_reports')
    revision_requested_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} - {self.club_id.name} - {self.reporting_period_id.label}"
    

class reports_info(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_id = models.ForeignKey(club_reports, on_delete=models.PROTECT)
    impact_metrics = models.JSONField(null=True, blank=True)
    featured_homepage = models.BooleanField(default=False)
    funds_raised = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    rp_doc_link = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Report Info for {self.report_id.id}"


class report_comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_id = models.ForeignKey(club_reports, on_delete=models.PROTECT)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    author_id = models.ForeignKey(users, on_delete=models.PROTECT)
    comment = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_comments')
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Comment by {self.author_id.name} on Report {self.report_id.id}"
    

class event_types(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    code = models.CharField(max_length=255, unique=True)
    label = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

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
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    event_type_id = models.ForeignKey(event_types, on_delete=models.PROTECT)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models. PROTECT)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = EncryptedTextField()
    planned_date = models.DateTimeField()
    actual_date = models.DateTimeField(null=True, blank=True)
    planned_start_time = models.TimeField()
    venue = models.CharField(max_length=255)
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(max_length=500, null=True, blank=True)
    attendees = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=255, choices=EVENT_STATUS_CHOICES, default="draft")
    is_public = models.BooleanField(default=False)
    patner_clubs = models.ManyToManyField(clubs, related_name='partner_clubs', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_events')  
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_events')  
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


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
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    focus_area = models.ForeignKey(rotary_focus_areas, null=True, blank=True, on_delete=models. PROTECT)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = EncryptedTextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    beneficiary_type = models.CharField(max_length=255, choices=BENEFICIARY_TYPE_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=255, choices=EVENT_STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)    
    created_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_projects')  
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_projects')  
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.club_id.name} - {self.start_date}"

CONTENT_TYPE_CHOICES = [
    ("report", "Report"),
    ("event", "Event"),
    ("project", "Project"),
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
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)

    context_type = models.CharField(max_length=255, choices=CONTENT_TYPE_CHOICES)
    context_id = models.UUIDField(null=False, blank=False)
    storage_provider = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=255)
    public_url = models.URLField(max_length=500)

    file_type = models.CharField(max_length=255, choices=FILE_TYPE_CHOICES)
    file_size = models.PositiveIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    hash_code = models.CharField(max_length=255, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_media')
    uploaded_by = models.ForeignKey(users, null=True, blank=True, on_delete=models.SET_NULL, related_name='uploaded_media')
    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    district_id = models.ForeignKey(districts, on_delete=models.PROTECT)
    club_id = models.ForeignKey(clubs, on_delete=models.PROTECT)
    actor_id = models.ForeignKey(users, on_delete=models.PROTECT)
    activity_type = models.CharField(max_length=255, choices=ACTIVITY_TYPE_CHOICES)
    entity_type = models.CharField(max_length=255)
    entity_id = models.UUIDField()
    summary = models.CharField(max_length=500)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Activity {self.activity_type} by {self.actor_id.name} at {self.created_at}"

