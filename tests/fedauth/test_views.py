from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.cache import SessionStore
from django.core.cache import cache as default_cache  # to prevent fixture clash
from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from fedauth.views import AuthenticationCallbackView
from tests.base import FakeRequest, FakeToken


class TestAuthenticationCallbackView(TestCase):

    def setUp(self):
        self.callback_view = AuthenticationCallbackView()
        # set up ongoing request
        self.callback_view.request = FakeRequest
        self.callback_view.request.user = get_user_model().objects.create(
            username='random@guy.com'
        )
        # populate session with context data
        self.failure_url = 'https://some_site.com/landing/'
        self.success_url = 'https://some_site.com/home/'
        self.callback_view.request.session['fail'] = self.failure_url
        self.callback_view.request.session['next'] = self.success_url

    def tearDown(self):
        # clear any sessions left over by tests.
        default_cache.clear()

    @staticmethod
    def create_session(key, extra_data: dict) -> None:
        """
        Helper to create a session.
        :param key: the session key
        :param extra_data: dict containing extra session context data
        :return: None
        """
        session = SessionStore(key)
        session._session_key = key
        session.save(must_create=True)
        for k, v in extra_data.items():
            session[k] = v
        session.save()

    def test_default_success_url_for_admin_login_callback(self):
        """
        For admin login, there is no 'next' url in session. We should instead use default login redirect url, which
        is configured in settings: 'LOGIN_REDIRECT_URL'
        """
        self.callback_view.request.session.clear()  # clear session created in init
        assert self.callback_view.success_url == settings.LOGIN_REDIRECT_URL

    def test_default_failure_url_for_admin_login_callback(self):
        """
        For admin login, there is no 'fail' url in session. We should instead use default redirect url, which
        is configured in settings: 'LOGIN_REDIRECT_URL_FAILURE'
        """
        self.callback_view.request.session.clear()   # clear session created in init
        assert self.callback_view.success_url == settings.LOGIN_REDIRECT_URL_FAILURE

    @mock.patch('fedauth.views.secrets.token_urlsafe')
    @mock.patch('rest_framework_simplejwt.tokens.RefreshToken.for_user')
    def test_success_url_for_frontend_login_callback(self, jwt, code):
        """
        For frontend login, there is a 'next' url in session, which is the redirect url.
        """
        jwt.return_value = FakeToken()
        urlsafe_code = 'uTOp_UWMd_4gaBwjhS1aIvvP7it95b3NoHK1xIlBrHY'
        code.return_value = urlsafe_code
        # assert that session contains 'next' context
        assert self.callback_view.request.session.get('next')

        # assert that success url matches the session 'next' url
        assert self.callback_view.success_url == (
            'https://some_site.com/home/?'
            f'code={urlsafe_code}'
        )
        # assert that tokens are stored in cache with code as key
        assert default_cache.get(f'auth_code:{urlsafe_code}') == {'access_token': 'access', 'refresh_token': 'refresh'}

        # 'next' url should be removed from session after url is successfully crafter by success_url property
        assert not self.callback_view.request.session.get('next')

    def test_failure_url_for_frontend_login_callback(self):
        """
        For frontend login, there is a 'fail' url in session, which is the redirect url.
        """
        # assert that session contains 'fail' context
        assert self.callback_view.request.session.get('fail')
        assert self.callback_view.failure_url == self.failure_url
        # 'fail' url should be removed from session after url is successfully crafter by failure_url property
        assert not self.callback_view.request.session.get('fail')

    def test_retrieve_session_by_id(self):
        """
        Test that 'retrieve_session_by_id retrieves the correct session.
        """
        # create a session, and add some data
        session_key = 'this_is_the_key'
        data = {'test': 'data'}
        self.create_session(session_key, data)
        session = self.callback_view.retrieve_session_by_id(session_key)
        assert session == data

    @mock.patch('mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get')
    def test_get_with_state_matching_session_id(self, get_method):
        """
        With frontend login attempts, the state parameter is set to equal the session id.
        The session then should be restored.
        """
        client = Client()
        # mock getting a redirect from get call
        get_method.return_value = HttpResponseRedirect(self.success_url)

        # create a frontend-backend session that would have been created during initial login api from fe to be
        fe_session_key = 'this_is_the_session_key_for_fe_session'
        self.create_session(fe_session_key, {'data': 'extra context data'})

        # during get call, the sessions should be restored
        callback_url = reverse('oidc-provider-callback')
        resp = client.get(f'{callback_url}?state={fe_session_key}')  # state that matched original session id
        assert resp.status_code == 302
        # session should now be the "restored" frontend-backend session
        assert resp.wsgi_request.session._session_key == fe_session_key
        assert resp.wsgi_request.session._session_cache == {'data': 'extra context data'}

    @mock.patch('mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get')
    def test_get_with_random_state(self, get_method):
        """
        Admin logins doesn't need to set state=session_id as with frontend logins, so for these we just check
        that get still work as expected if there is no matching session.
        """
        client = Client()
        # mock getting a redirect from get call
        get_method.return_value = HttpResponseRedirect(self.success_url)
        # client.request.session = provider_session
        callback_url = reverse('oidc-provider-callback')
        # make the state param a random string (not matching any session id)
        resp = client.get(f'{callback_url}?state={get_random_string(32)}')
        assert resp.status_code == 302
        # No session id, means it didn't try to restore any session.
        assert not resp.wsgi_request.session._session_key
