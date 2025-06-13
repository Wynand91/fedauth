from django.urls import path, include

from fedauth.views import AuthenticationCallbackView

urlpatterns = [
    path('callback/', AuthenticationCallbackView.as_view(), name='oidc-provider-callback'),
    path('authenticate/', include('fedauth.dynamic_oidc.urls')),
    path('login/', include('fedauth.frontend_oidc.urls'))
]
