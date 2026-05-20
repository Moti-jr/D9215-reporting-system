from django.db import models
from django.utils import timezone
import uuid


class UserCredential(models.Model):
	"""Stores password hashes for users in `public.user_credentials`.

	Note: This table is separate from `public.users` and maps by `user_id`.
	"""
	user_id = models.UUIDField(primary_key=True)
	password_hash = models.CharField(max_length=255)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		db_table = 'user_credentials'


class Session(models.Model):
	"""Maps to the existing `public.sessions` table for token revocation.
	We store the token identifier (jti) in `token_hash` for revocation checks.
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user_id = models.UUIDField()
	token_hash = models.CharField(max_length=255, unique=True)
	ip_address = models.CharField(max_length=45, null=True)
	user_agent = models.CharField(max_length=500, null=True)
	expires_at = models.DateTimeField()
	revoked_at = models.DateTimeField(null=True)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		db_table = 'sessions'
