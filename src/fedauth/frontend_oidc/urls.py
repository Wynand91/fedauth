from django.urls import path

from fedauth.frontend_oidc.api.views import OidcLoginView

urlpatterns = [
    path('', OidcLoginView.as_view(), name='oidc-provider-login')
]
