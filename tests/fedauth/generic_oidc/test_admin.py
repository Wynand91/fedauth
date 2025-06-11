from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse

from fedauth.admin import GenericProviderAdmin
from fedauth.crypto import decrypt
from fedauth.models import GenericProvider
from tests.base import FakeRequest
from tests.factories import GenericProviderFactory


class TestGenericProviderAdmin(TestCase):

    def setUp(self):
        self.superuser = get_user_model().objects.create(
            username='admin',
            is_superuser=True,
            is_staff=True,
        )
        self.client.force_login(self.superuser)
        self.admin = GenericProviderAdmin(GenericProvider, AdminSite())
        self.create_url = reverse('admin:fedauth_genericprovider_add')
        self.gp = GenericProviderFactory()

    def test_get_fields(self):
        # client_secret should not be included for read fields (object exists)
        assert 'client_secret' not in self.admin.get_fields(FakeRequest, self.gp)

        # client should be included for write (no object yet)
        assert 'client_secret' in self.admin.get_fields(FakeRequest, None)

    def test_create_gp_object_failure(self):
        resp = self.client.post(self.create_url, {})
        assert resp.status_code == 200
        assert ['This field is required.'] in resp.context_data['errors']

    def test_create_gp_already_exists(self):
        provider = 'jumpcloud'
        client_secret = 'KFcP.k4GmTqCv2.9HtB3Dp2~3q'
        resp = self.client.post(self.create_url, {
            'provider': provider,
            'auth_endpoint': 'https://some.ip.com/auth/',
            'token_endpoint': 'https://some.ip.com/token/',
            'user_endpoint': 'https://some.ip.com/user/',
            'jwks_endpoint': 'https://some.ip.com/keys/',
            'client_id': 'c9e1ee6c-9755-9755-ac86-5e7b657f4d53',
            'client_secret': client_secret,
            'sign_algo': 'RS256',
            'scopes': "openid profile email phone groups",
        })
        # jumpcloud provider already exists, so should het a 200 response and errors on the form
        assert resp.status_code == 200
        form = resp.context['adminform'].form
        assert form.errors == {'provider': ['Generic provider with this Provider already exists.']}

    def test_create_gp_save(self):
        provider = 'okta'
        client_secret = 'KFcP.k4GmTqCv2.9HtB3Dp2~3q'
        resp = self.client.post(self.create_url, {
            'provider': provider,
            'auth_endpoint': 'https://some.ip.com/auth/',
            'token_endpoint': 'https://some.ip.com/token/',
            'user_endpoint': 'https://some.ip.com/user/',
            'jwks_endpoint': 'https://some.ip.com/keys/',
            'client_id': 'c9e1ee6c-9755-9755-ac86-5e7b657f4d53',
            'client_secret': client_secret,
            'sign_algo': 'RS256',
            'scopes': "openid profile email phone groups",
        })
        assert resp.status_code == 302
        new_gp = GenericProvider.objects.get(provider=provider)
        # check that client secret is saved and encrypted
        encrypted_secret = new_gp.client_secret_cipher
        assert decrypt(encrypted_secret).decode() == client_secret
