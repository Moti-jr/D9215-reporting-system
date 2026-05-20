from django.test import TestCase, Client
import django
from django.contrib.auth.hashers import make_password
import json

from .models import UserCredential


class AuthFlowTests(TestCase):
	def setUp(self):
		self.client = Client()

		# create credential for user
		self.user_id = '11111111-1111-1111-1111-111111111111'
		UserCredential.objects.create(user_id=self.user_id, password_hash=make_password('secret'))

	def test_login_and_access(self):
		# request token
		resp = self.client.post('/api/auth/login/', data=json.dumps({'user_id': self.user_id, 'password': 'secret'}), content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		data = resp.json()
		token = data.get('access_token')
		self.assertTrue(token)

		# call protected endpoint
		auth_header = 'Bearer ' + token
		resp2 = self.client.get('/test/protected/', HTTP_AUTHORIZATION=auth_header)
		self.assertEqual(resp2.status_code, 200)
		payload = resp2.json()
		self.assertEqual(payload.get('sub'), self.user_id)

