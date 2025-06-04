from django.contrib.auth.views import LoginView as _LoginView
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from fedauth.federated_providers.models import FederatedProvider
from fedauth.oidc_admin.forms import UsernameForm


class LoginView(_LoginView):
    """
    Overrides django's default LoginView to do domain lookups for federated logins.
    """
    template_name = 'admin/oidc_login.html'
    authentication_form = UsernameForm

    def get_template_names(self):
        """
        Check if user has custom template configured, else use default
        """
        template = getattr(settings, "LOGIN_TEMPLATE", self.template_name)
        return [template]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            username = form.cleaned_data['username']
            domain = username.split('@')[-1]
            db_provider_exists = FederatedProvider.objects.filter(domain=domain).exists()
            # 'db-provider-auth' for OIDC authentication flow, 'admin-login-default' for standard django auth flow
            view_name = 'db-provider-auth' if db_provider_exists else 'admin-login-default'
            # store some details in session storage. Needed during OIDC callback.
            request.session['domain'] = domain
            url = reverse(view_name, kwargs={'username': username})
            return redirect(url)
        return self.form_invalid(form)


class DefaultLoginView(_LoginView):
    """
    Default login view with small change to pick up username to pre-populate form. Username can be stored in
    request session before redirect to this class.
    """

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        form = self.form_class(initial={'username': username})
        return self.render_to_response({'form': form})
