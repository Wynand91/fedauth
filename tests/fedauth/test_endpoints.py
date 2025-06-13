from django.urls import reverse_lazy

from tests.base import BaseApiTestCase
from tests.factories import StaticProviderFactory


class TestOidcAuthEndpoints(BaseApiTestCase):

    def setUp(self):
        self.static_provider = StaticProviderFactory()
        self.auth_url = reverse_lazy('jumpcloud_authentication_init')
        self.callback_url = reverse_lazy('oidc-provider-callback')

    def test_authenticate_redirect(self):
        resp = self.get(self.auth_url)
        assert resp.status_code == 302  # redirect
        # crafted url should start with models 'auth_endpoint'
        assert resp.url.startswith('https://oauth.id.jumpcloud.com/oauth2/auth')

    def test_callback(self):
        # not testing functionality, only that settings are obtained correctly.
        resp = self.get(self.callback_url)
        assert resp.status_code == 302  # redirect
        assert resp.url == '/'
