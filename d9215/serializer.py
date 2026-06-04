from .models import (
    audit_logs,
    clubs,
    districts,
    rotary_focus_areas,
    users,
    club_activity_feed,
    reporting_periods,
    club_reports,
    reports_info,
    report_comments,
    event_types,
    events,
    projects,
    media_assets
)
from rest_framework import serializers

class audit_logs_Serializer(serializers.ModelSerializer):
    class Meta:
        model = audit_logs
        fields = '__all__'

class rotary_focus_areas_Serializer(serializers.ModelSerializer):
    class Meta:
        model = rotary_focus_areas
        fields = '__all__'

class districts_Serializer(serializers.ModelSerializer):
    class Meta:
        model = districts
        fields = '__all__'

class clubs_Serializer(serializers.ModelSerializer):
    class Meta:
        model = clubs
        fields = '__all__'

class users_Serializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = '__all__'

class club_activity_feed_Serializer(serializers.ModelSerializer):
    class Meta:
        model = club_activity_feed
        fields = '__all__'

class reporting_periods_Serializer(serializers.ModelSerializer):
    class Meta:
        model = reporting_periods
        fields = '__all__'

class club_reports_Serializer(serializers.ModelSerializer):
    class Meta:
        model = club_reports
        fields = '__all__'

class reports_info_Serializer(serializers.ModelSerializer):
    class Meta:
        model = reports_info
        fields = '__all__'

class report_comments_Serializer(serializers.ModelSerializer):
    class Meta:
        model = report_comments
        fields = '__all__'

class event_types_Serializer(serializers.ModelSerializer):
    class Meta:
        model = event_types
        fields = '__all__'

class events_Serializer(serializers.ModelSerializer):
    class Meta:
        model = events
        fields = '__all__'

class projects_Serializer(serializers.ModelSerializer):
    class Meta:
        model = projects
        fields = '__all__'

class media_assets_Serializer(serializers.ModelSerializer):
    class Meta:
        model = media_assets
        fields = '__all__'




