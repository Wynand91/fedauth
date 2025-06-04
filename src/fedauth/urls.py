from django.urls import path, include

from fedauth.views import AuthenticationCallbackView

urlpatterns = [
    path('callback/', AuthenticationCallbackView.as_view(), name='oidc-provider-callback'),
    path('authenticate/', include('fedauth.federated_providers.urls')),
    path('login/', include('fedauth.frontend_oidc.urls'))
]
