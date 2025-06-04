from django.contrib.sessions.backends.cache import SessionStore
from django.shortcuts import resolve_url
from mozilla_django_oidc.views import (
    OIDCAuthenticationCallbackView
)
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationCallbackView(OIDCAuthenticationCallbackView):
    """
    This is the callback view that will be called by ALL idP after a user successfully authenticates on the idP.
    The baseclass `get` method calls auth.authenticate(), which in turns calls The Auth backend defined in
    settings (AUTHENTICATION_BACKENDS), which will handle user creation/update/authentication.
    """

    @property
    def failure_url(self):
        # check if different failure redirect url is set (during frontend login), else assume admin login flow,
        # and redirect to LOGIN_REDIRECT_URL_FAILURE
        next_url = self.request.session.get('fail')
        self.request.session.pop('fail', None)  # remove from session storage
        return next_url or self.get_settings('LOGIN_REDIRECT_URL_FAILURE', '/')

    @property
    def success_url(self):
        # if frontend login ('oidc_login_next' in session), generate tokens and return as url query params
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

    @staticmethod
    def restore_session(request, session_data, session_id):
        """
        Replaces a request session with another session. This is used to fuse the frontend-backend session
        with the OIDC provider/backend session
        """
        # Assign the session data to the current request's session
        request.session.clear()
        request.session.update(session_data)
        request.session.modified = True

        # Set the session key (session ID) to match the original session
        request.session._session_key = session_id

    def get(self, request):
        """
        During the login (API) oidc flow, there's a disconnect between the initial login request session (between
        frontend and backend) and the callback request session (between OIDC provider and backend), since the OIDC
        authentication call to the OIDC provider is initiated from outside the backend ecosystem. This means
        that all context added to the request session during auth url building, is lost by the time the callback
        happens.
        In order to work around this, we need to marry the sessions (as if though the authenticate request occurred
        from inside the backend). During the initial login request, we assign the session id as the 'state'
        parameter, since the 'state' param is the only value that is persisted throughout the entire auth flow. Thus,
        when we get to this callback method, we can look up the original request session, and merge the two requests
        sessions into a single request session, thereby retaining all the values stored in the original request session,
        and authenticate the correct user.
        """
        state = request.GET.get('state')

        # check if a session id exists that matches the state key
        session_data = self.retrieve_session_by_id(state)
        if session_data:
            self.restore_session(request, session_data, state)

        return super().get(request)
