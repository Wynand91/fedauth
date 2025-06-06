from django.urls import path

from fedauth.frontend_oidc.api.views import OidcLoginView, TokenExchangeView

urlpatterns = [
    path('', OidcLoginView.as_view(), name='oidc-provider-login'),
    path('token-exchange/', TokenExchangeView.as_view(), name='token-exchange')
]
