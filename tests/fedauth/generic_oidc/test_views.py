from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from fedauth.generic_oidc.models import GenericProvider
from fedauth.generic_oidc.views import GenericAuthenticationRequestView
from tests.factories import GenericProviderFactory


class TestAuthenticationRequestView(TestCase):

    def setUp(self):
        self.prov = 'fb'
        self.request_view = GenericAuthenticationRequestView()
        self.request_view.alias = self.prov
        self.gen_provider = GenericProviderFactory(provider=self.prov)

    def test_auth_request_view_get_settings(self):
        # class attributes should be None after init. Only gets set in get request flow
        assert not self.request_view.OIDC_OP_AUTH_ENDPOINT
        assert not self.request_view.OIDC_RP_CLIENT_ID

        # If config is not found on mode, but a default is passed, the default value should be returned.
        assert self.request_view.get_settings('OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS', 60 * 15) == 900
        assert self.request_view.get_settings('OIDC_STATE_SIZE', 32) == 32

    def test_auth_request_view_get_invalid_settings(self):
        # error should be raise if config doesn't exist, and no default is passed
        with self.assertRaises(ImproperlyConfigured) as error:
            assert self.request_view.get_settings('NON_EXISTING_SETTINGS')
        assert str(error.exception) == "Setting NON_EXISTING_SETTINGS not found for provider: 'fb'"
