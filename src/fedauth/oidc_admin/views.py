from django.contrib.auth.views import LoginView as DjangoLoginView
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from fedauth.federated_oidc.models import FederatedProvider
from fedauth.oidc_admin.forms import UsernameForm


class LoginView(DjangoLoginView):
    """
    This view is used instead of the default django admin login view, so that we can do federation checks on
    username
    """
    template_name = 'admin/oidc_login.html'
    authentication_form = UsernameForm

    def get_template_names(self):
        """
        Override template if user created a custom login template.
        """
        template = getattr(settings, 'LOGIN_TEMPLATE', self.template_name)
        return [template]

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # 1. get domain from username
            username = form.cleaned_data['username']
            domain = username.split('@')[-1]
            # 2. check if there is a federated provider object that matches domain
            db_provider_exists = FederatedProvider.objects.filter(domain=domain).exists()
            # 3. Determine which view to redirect to
            # 'fed-provider-auth' for OIDC authentication flow, 'default-admin-login' for standard django auth flow
            if db_provider_exists:
                next_view = 'fed-provider-auth'
                request.session['domain'] = domain  # Needed during OIDC callback.
            else:
                next_view = 'default-admin-login'
            # 4. redirect to next url with username as context (needed for both flows)
            url = reverse(next_view, kwargs={'username': username})
            return redirect(url)
        return self.form_invalid(form)


class DefaultLoginView(DjangoLoginView):
    """
    This is the Default login view, but since we'll have the username, we can pre-populate username field.
    """
    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        form = self.form_class(initial={'username': username})
        return self.render_to_response({'form': form})
