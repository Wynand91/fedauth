from django.contrib.sessions.backends.cache import SessionStore
from django.shortcuts import resolve_url
from mozilla_django_oidc.views import (
    OIDCAuthenticationCallbackView
)
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationCallbackView(OIDCAuthenticationCallbackView):
    """
    This is the callback view that will be called by ALL idP after a user successfully authenticates on the idP.
    The baseclass `get` method calls call auth.authenticate(), which in turns calls The Auth backend defined in
    settings (AUTHENTICATION_BACKENDS), which will handle user creation/update/authentication.
    """
    @property
    def failure_url(self):
        # 'fail' url will only be set/present if the flow originated from the frontend. If there is no next url, then
        # we can safely assume that we are busy with an admin login.
        next_url = self.request.session.get('fail')
        self.request.session.pop('fail', None)  # remove from session storage
        return next_url or self.get_settings('LOGIN_REDIRECT_URL_FAILURE', '/')

    @property
    def success_url(self):
        # if frontend login ('oidc_login_next' in session), generate tokens and return as url query params
        # todo: instead of returning token, return a code that can then be exchanged for a token.
        next_url = self.request.session.get('next', None)
        if next_url:
            tokens = RefreshToken.for_user(user=self.request.user)
            refresh_token = str(tokens)
            access_token = str(tokens.access_token)  # NOQA
            next_url = f'{next_url}?access={access_token}&refresh={refresh_token}'
            self.request.session.pop('next', None)  # remove from session storage
        return next_url or resolve_url(self.get_settings('LOGIN_REDIRECT_URL', '/'))

    @staticmethod
    def retrieve_session_by_id(session_id):
        session_store = SessionStore(session_key=session_id)
        if session_store.exists(session_id):
            return session_store.load()
        return None

    def get(self, request):
        """
        If oidc flow originates from frontend (via API), then there will be 2 separate sessions in play ny the time
        this callback is called by the idP. There will be:
        1 session between frontend and backend (session A)
        1 session between backend and idP (session B)
        This is a problem, because the session between frontend and backend contains all the OIDC context that is needed
        during callback to authenticate the correct user, and since session B is a different session altogether,
        we don't have the context during the callback. Yikes.

        This is where we need to introduce some magic. The OIDC flow provides as with a solution. There is a 'state'
        parameter that is persisted throughout the entire OIDC flow (url parameter, so not tied to session).
        We can set this state during the initial login request.

        So we set our initial session ID as the state parameter! Then, during the callback, we can retrieve the original
        session using the state parameter, and join the two sessions into one, thereby providing all the OIDC context
        that is needed for the callback authentication to happen.
        """
        state = request.GET.get('state')
        session_data = self.retrieve_session_by_id(state)  # retrieve original session
        if session_data:
            request.session.clear()
            request.session.update(session_data)
            request.session.modified = True
            request.session._session_key = state
        return super().get(request)
