from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.backends.cache import SessionStore
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from fedauth.views import AuthenticationCallbackView
from tests.base import FakeRequest, FakeToken


class TestAuthenticationCallbackView(TestCase):

    def setUp(self):
        cache.clear()
        self.callback_view = AuthenticationCallbackView()
        self.callback_view.request = FakeRequest
        self.callback_view.request.user = User.objects.create(username='some@user.com')
        # load some values into session
        self.fail_url = 'https://frontend.com/login/'
        self.success_url = 'https://frontend.com/home/'
        self.callback_view.request.session['fail'] = self.fail_url
        self.callback_view.request.session['next'] = self.success_url

    def test_default_success_url(self):
        """
        If there is no 'next' url in session, default config should be used - this is the default flow
        for admin logins
        """
        self.callback_view.request.session.clear()
        assert not self.callback_view.request.session.get('next')
        success_url = self.callback_view.success_url
        assert success_url == settings.LOGIN_REDIRECT_URL

    def test_default_failure_url(self):
        """
        If there is no 'fail' url in session, default config should be used - this is the default flow
        for admin logins
        """
        self.callback_view.request.session.clear()
        assert not self.callback_view.request.session.get('fail')
        success_url = self.callback_view.success_url
        assert success_url == settings.LOGIN_REDIRECT_URL_FAILURE

    @mock.patch('rest_framework_simplejwt.tokens.RefreshToken.for_user')
    def test_success_url(self, jwt):
        """
        If there is a 'next' url in session, it should be the redirect url - this is the Login API flow.
        The success_url method should generate jwt tokens and return them as url query params
        """
        jwt.return_value = FakeToken()
        assert self.callback_view.request.session.get('next')

        success_url = self.callback_view.success_url
        assert success_url == (
            'https://frontend.com/home/?'
            'access=access'
            '&refresh=refresh'
        )
        # 'next' url should be removed from session
        assert not self.callback_view.request.session.get('next')

    def test_failure_url(self):
        """
        If there is a 'fail' url in session, it should be the redirect url - this is the Login API flow.
        """
        assert self.callback_view.request.session.get('fail')
        failure_url = self.callback_view.failure_url
        assert failure_url == self.fail_url
        # 'fail' url should be removed from session
        assert not self.callback_view.request.session.get('fail')

    def test_retrieve_session_by_id(self):
        # create a session, and add some data
        session_key = 'session_key'
        session = SessionStore(session_key)
        session._session_key = session_key
        session.save(must_create=True)
        session['test'] = 'value'
        session.save()
        # assert that correct session is retrieved with session id
        session = self.callback_view.retrieve_session_by_id(session_key)
        assert session == {'test': 'value'}

    def test_restore_session(self):
        """
        Once provider hits our callback, the request session should be merged with original fronted-backend
        request session.
        """
        # create frontend-backend session
        frontend_session_key = 'fe_session_key'
        frontend_session = SessionStore(frontend_session_key)
        frontend_session._session_key = frontend_session_key
        frontend_session.save(must_create=True)
        frontend_session['fe'] = 'data'
        frontend_session.save()

        # create provider-backend session
        provider_session_key = 'p_session_key'
        provider_session = SessionStore(provider_session_key)
        provider_session._session_key = provider_session_key
        provider_session.save(must_create=True)
        provider_session['provider'] = 'data'
        provider_session.save()

        request = FakeRequest
        request.session = provider_session
        # assert that the request session is indeed the provider-backend session
        assert request.session._session_key == 'p_session_key'
        assert request.session._session_cache == {'provider': 'data'}

        frontend_session_data = self.callback_view.retrieve_session_by_id(frontend_session_key)
        self.callback_view.restore_session(request, frontend_session_data, frontend_session_key)

        # request session should now be replaced by frontend session
        assert request.session._session_key == 'fe_session_key'
        assert request.session._session_cache == {'fe': 'data'}

    @mock.patch('mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get')
    def test_get_with_existing_state_session_key(self, base_get):
        """
        During login API flow, the state gets set to reflect the session id, so that session
        can be looked up during callback
        """
        base_get.return_value = HttpResponseRedirect(self.success_url)
        # mock frontend-backend session
        frontend_session_key = 'fe_session_key'
        frontend_session = SessionStore(frontend_session_key)
        frontend_session._session_key = frontend_session_key
        frontend_session.save(must_create=True)
        frontend_session['fe'] = 'data'
        frontend_session.save()

        client = Client()
        # client.request.session = provider_session
        url = reverse('oidc-provider-callback')
        resp = client.get(f'{url}?state={frontend_session_key}')
        assert resp.status_code == 302  # redirect
        # session should now be the "restored" frontend-backend session
        assert resp.wsgi_request.session._session_key == frontend_session_key
        assert resp.wsgi_request.session._session_cache == {'fe': 'data'}

    @mock.patch('mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get')
    def test_get_with_non_existing_state_session_key(self, base_get):
        """
        During admin login flow, the state is a random generated string, so does not reflect any
        existing session ids.
        """
        base_get.return_value = HttpResponseRedirect(self.success_url)
        client = Client()
        # client.request.session = provider_session
        url = reverse('oidc-provider-callback')
        resp = client.get(f'{url}?state={get_random_string(32)}')  # state is not an existing session id
        assert resp.status_code == 302  # redirect
        # session id should not be populated, since it wasn't manually populated, i.e. no restoration of
        # existing sessions
        assert not resp.wsgi_request.session._session_key
