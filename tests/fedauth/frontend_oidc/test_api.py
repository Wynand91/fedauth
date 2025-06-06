import secrets
from urllib.parse import urlencode, urlparse, parse_qs

from django.contrib.sessions.backends.cache import SessionStore
from django.core.cache import cache as default_cache  # to prevent fixture clash
from django.test import override_settings
from django.urls import reverse

from tests.base import BaseApiTestCase
from tests.factories import FederatedProviderFactory, GenericProviderFactory

FRONTEND_URL = 'www.fronted.com'


@override_settings(OIDC_REDIRECT_ALLOWED_HOSTS=[FRONTEND_URL])
class TestLoginApi(BaseApiTestCase):

    def setUp(self):
        self.fp = FederatedProviderFactory(domain='hogwarts.com')
        self.gp = GenericProviderFactory(provider='okta')
        self.login_url = reverse('oidc-provider-login')
        self.valid_url = f'https://{FRONTEND_URL}'
        self.invalid_url = 'fake_url'
        self.full_url = self.craft_full_login_url()

    def craft_full_login_url(self):
        query_params = {
            'next': self.valid_url,
            'fail': self.valid_url
        }
        params = urlencode(query_params)
        return f'{self.login_url}?{params}'

    def test_login_no_data(self):
        data = {}
        resp = self.post(url=self.full_url, data=data)
        assert resp.status_code == 400
        assert resp.json() == {'non_field_errors': ['Must submit either username OR provider']}

    def test_login_invalid_provider(self):
        data = {'provider': 'invalid_provider'}
        resp = self.post(url=self.full_url, data=data)
        assert resp.status_code == 400
        assert resp.json() == {'provider': ['"invalid_provider" is not a valid choice.']}

    def test_login_username_and_provider(self):
        data = {
            'username': 'dobby@hogwarts.com',
            'provider': 'okta'
        }
        resp = self.post(url=self.full_url, data=data)
        assert resp.status_code == 400
        assert resp.json() == {'non_field_errors': ['Submit either username OR provider, not both.']}


    def test_login_missing_url_param_validation(self):
        resp = self.post(url=self.login_url, data={})
        assert resp.status_code == 400
        assert resp.json() == ["Missing 'next' and/or 'fail' url parameters"]

    def test_login_invalid_url_param_validation(self):
        invalid_next_query_params = {
            'next': self.invalid_url,
            'fail': self.valid_url
        }
        url = f'{self.login_url}?{urlencode(invalid_next_query_params)}'
        resp = self.post(url=url, data={})
        assert resp.status_code == 400
        assert resp.json() == ["Invalid 'next' or 'success' url"]

        invalid_fail_query_params = {
            'next': self.valid_url,
            'fail': self.invalid_url
        }
        url = f'{self.login_url}?{urlencode(invalid_fail_query_params)}'
        resp = self.post(url=url, data={})
        assert resp.status_code == 400
        assert resp.json() == ["Invalid 'next' or 'success' url"]

    def test_login_username_request_success(self):
        """
        if post data contains 'username', we know it's a federated OIDC flow
        """
        data = {'username': 'hagrid@hogwarts.com'}
        resp = self.post(url=self.full_url, data=data)
        assert resp.status_code == 200
        json = resp.json()
        auth_url = json.get('auth_url')
        assert auth_url
        assert auth_url.startswith(self.fp.auth_endpoint)

        # assert that generated url's "state" param matches an existing session.
        parsed_url = urlparse(auth_url)
        state = parse_qs(parsed_url.query)['state'][0]
        session_store = SessionStore(session_key=state)
        assert session_store.exists(state)

        # check that appropriate values are stored in session
        session = session_store.load()
        assert session.get('domain') == 'hogwarts.com'
        assert session.get('next') == self.valid_url
        assert session.get('fail') == self.valid_url

        # double check that provider isn't in session (since not a generic oidc login request)
        assert not session.get('provider')

    def test_login_generic_provider_request_success(self):
        """
        if post data contains 'provider', we know it's a generic OIDC flow (e.g. 'login with Facebook')
        """
        provider = 'okta'
        data = {'provider': provider}
        resp = self.post(url=self.full_url, data=data)
        assert resp.status_code == 200
        json = resp.json()
        auth_url = json['auth_url']
        assert auth_url
        assert auth_url.startswith(self.gp.auth_endpoint)

        # assert that generated url's "state" param matches an existing session.
        parsed_url = urlparse(auth_url)
        state = parse_qs(parsed_url.query)['state'][0]
        session_store = SessionStore(session_key=state)
        assert session_store.exists(state)

        # check that session contains all the values that is needed for callback
        session = session_store.load()
        assert session.get('provider') == 'okta'
        assert session.get('next') == self.valid_url
        assert session.get('fail') == self.valid_url

        # double check that domain isn't in session (since not a federated login request)
        assert not session.get('domain')


class TestTokenExchangeApi(BaseApiTestCase):

    def setUp(self):
        self.url = reverse('token-exchange')

        # mock tokens saved in cache by callback API
        self.valid_code = secrets.token_urlsafe(32)
        self.jwt_data = {
            'access_token': 'this.is.the.access.token',
            'refresh_token': 'this.is.the.refresh.token'
        }
        default_cache.set(
            f'auth_code:{self.valid_code}',
            self.jwt_data
        )

    def test_exchange_invalid_code_length(self):
        data={'code': 'expired_code' * 6}
        resp = self.post(self.url, data=data)
        assert resp.status_code == 400
        assert resp.json() == {'code': ['Ensure this field has no more than 64 characters.']}

    def test_exchange_invalid_code(self):
        data={'code': 'expired_code'}
        resp = self.post(self.url, data=data)
        assert resp.status_code == 400
        assert resp.json() == {'detail': ['Code Invalid or expired']}

    def test_exchange_valid_code(self):
        data={'code': self.valid_code}
        resp = self.post(self.url, data=data)
        assert resp.status_code == 200
        assert resp.json() == self.jwt_data
