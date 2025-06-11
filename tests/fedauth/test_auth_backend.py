from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from fedauth.backends import OIDCAuthenticationBackend
from fedauth.models import FederatedProvider
from tests.base import FakeRequest
from tests.factories import FederatedProviderFactory, GenericProviderFactory


class TestFederatedAuthenticationBackend(TestCase):
    """
    We need to test that the FProviderSettingsMixin overrides the way settings is obtained (normally it would
    be done via mozilla's default 'get_settings' method, but our mixin should override that)
    """
    def setUp(self):
        # set up federated provider obj
        self.domain = 'company.com'
        self.fed_provider: FederatedProvider = FederatedProviderFactory(domain=self.domain)
        # set up generic provider obj
        self.provider = 'jumpcloud'
        self.gen_provider: FederatedProvider = GenericProviderFactory(provider=self.provider)
        self.backend = OIDCAuthenticationBackend()
        self.backend.request = FakeRequest
        self.backend.request.session.clear()

    def test_no_settings_after_init(self):
        # since we skip config setup in the init, there should be no settings configured after class initialization in
        # test setUp method (should throw an error when trying to access attribute)
        with self.assertRaises(AttributeError):
            assert self.backend.OIDC_RP_CLIENT_ID

    def test_configure_oidc_settings_method(self):
        # the 'configure_oidc_settings' should retrieve and populate the class attributes
        self.backend.request.session['domain'] = self.domain  # method requires domain
        self.backend.configure_oidc_settings()
        assert self.backend.OIDC_OP_TOKEN_ENDPOINT == self.fed_provider.token_endpoint
        assert self.backend.OIDC_OP_USER_ENDPOINT == self.fed_provider.user_endpoint
        assert self.backend.OIDC_OP_JWKS_ENDPOINT == self.fed_provider.jwks_endpoint
        assert self.backend.OIDC_RP_CLIENT_ID == self.fed_provider.client_id
        assert self.backend.OIDC_RP_CLIENT_SECRET == self.fed_provider.client_secret
        assert self.backend.OIDC_RP_SIGN_ALGO == self.fed_provider.sign_algo

    def test_configure_oidc_settings_method_for_generic_provider(self):
        # the 'configure_oidc_settings' should retrieve and populate the class attributes
        # self.backend.request = FakeRequest
        self.backend.request.session['provider'] = self.provider   # method requires provider
        self.backend.configure_oidc_settings()
        assert self.backend.OIDC_OP_TOKEN_ENDPOINT == self.gen_provider.token_endpoint
        assert self.backend.OIDC_OP_USER_ENDPOINT == self.gen_provider.user_endpoint
        assert self.backend.OIDC_OP_JWKS_ENDPOINT == self.gen_provider.jwks_endpoint
        assert self.backend.OIDC_RP_CLIENT_ID == self.gen_provider.client_id
        assert self.backend.OIDC_RP_CLIENT_SECRET == self.gen_provider.client_secret
        assert self.backend.OIDC_RP_SIGN_ALGO == self.gen_provider.sign_algo

    @patch('fedauth.backends.OIDCAuthenticationBackend.configure_oidc_settings')
    @patch('mozilla_django_oidc.auth.OIDCAuthenticationBackend.authenticate')
    def test_authenticate_method(self, auth, configs):
        """
        Test that the 'configure_oidc_settings' method is called when 'authenticate' method is called.
        """
        request = FakeRequest
        request.session['domain'] = self.domain
        self.backend.authenticate(request)
        assert configs.called

    def test_session_storage_is_cleared(self):
        """
        After successful authentication, the 'filter_users_by_claims' method is called. This method should clear session
        storage, since values aren't needed anymore.
        """
        self.backend.request.session['domain'] = 'company.com'
        self.backend.request.session['provider'] = 'fb'
        # check that values are in session storage
        assert self.backend.request.session == {'domain': 'company.com', 'provider': 'fb'}
        self.backend.filter_users_by_claims({})
        # after 'filter_users_by_claims' runs, the values should be cleard.
        assert self.backend.request.session == {}

    def test_update_user(self):
        """
        the 'update_user' method updates user according to claims provider from idP.
        Claims returned from idP should be the source of truth for user attributes.
        """
        user = User.objects.create(username='user@test.com')
        assert not user.is_staff  # by default, user is not admin.
        # if the claims say user is admin, the user should be updated
        claims = {'groups': ['admin']}
        self.backend.update_user(user, claims)
        # user should now be admin, but not superuser
        assert user.is_staff
        assert not user.is_superuser

        # if the claims say user is admin and superuser
        claims = {'groups': ['admin', 'superuser']}
        self.backend.update_user(user, claims)
        assert user.is_staff
        # user should now also be superuser
        assert user.is_superuser

    def test_create_user(self):
        """
        When the user does not exist on the system yet, but authenticates via idP, we use the claims from idP
        to create a new user.
        """
        self.backend.request.session['provider'] = 'fb'
        username = 'user@test.com'
        # check that no user exists with this username
        assert not User.objects.filter(username=username).exists()

        claims = {'email': username, 'groups': ['admin', 'superuser']}
        self.backend.create_user(claims)
        # user should now exist with all claim attributes set
        user = User.objects.get(username=username)
        assert user.is_staff
        assert user.is_superuser
