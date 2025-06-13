from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse

from fedauth.admin import DynamicProviderAdmin
from fedauth.crypto import decrypt
from fedauth.models import DynamicProvider
from tests.base import FakeRequest
from tests.factories import DynamicProviderFactory


class TestDynamicOidcAdmin(TestCase):

    def setUp(self):
        self.super_user = get_user_model().objects.create(username='test', is_superuser=True, is_staff=True)
        self.client.force_login(self.super_user)
        self.admin = DynamicProviderAdmin(DynamicProvider, AdminSite())
        self.dynamic_provider = DynamicProviderFactory()
        self.create_url = reverse('admin:fedauth_dynamicprovider_add')

    def test_create_fp_object_failure(self):
        resp = self.client.post(self.create_url, {})
        assert resp.status_code == 200
        assert ['This field is required.'] in resp.context_data['errors']

    def test_create_fb_already_exists(self):
        domain = self.dynamic_provider.domain
        client_secret = 'topsecret'
        resp = self.client.post(self.create_url, {
            'domain': domain,
            'auth_endpoint': 'https://provider.com/auth/',
            'token_endpoint': 'https://provider.com/token/',
            'user_endpoint': 'https://provider.com/user/',
            'jwks_endpoint': 'https://provider.com/keys/',
            'client_id': 'a1123a67-1423-4124-24hg-7h12k124h3hj',
            'client_secret': client_secret,
            'sign_algo': 'RS256',
            'scopes': "openid profile email phone groups",
        })
        # domain already exists, so should het a 200 response and errors on the form
        assert resp.status_code == 200
        form = resp.context['adminform'].form
        assert form.errors == {'domain': ['Dynamic provider with this Domain already exists.']}

    def test_create_fp_save(self):
        domain = 'somecompany.com'
        client_secret = 'topsecret'
        resp = self.client.post(self.create_url, {
            'domain': domain,
            'auth_endpoint': 'https://provider.com/auth/',
            'token_endpoint': 'https://provider.com/token/',
            'user_endpoint': 'https://provider.com/user/',
            'jwks_endpoint': 'https://provider.com/keys/',
            'client_id': 'a1123a67-1423-4124-24hg-7h12k124h3hj',
            'client_secret': client_secret,
            'sign_algo': 'RS256',
            'scopes': "openid profile email phone groups",
        })
        assert resp.status_code == 302
        new_fp = DynamicProvider.objects.get(domain=domain)
        # check that client secret is saved and encrypted
        encrypted_secret = new_fp.client_secret_cipher
        assert decrypt(encrypted_secret).decode() == client_secret

    def test_client_secret_read(self):
        assert 'client_secret' not in self.admin.get_fields(FakeRequest, self.dynamic_provider)

    def test_client_secret_write(self):
        assert 'client_secret' in self.admin.get_fields(FakeRequest, None)
