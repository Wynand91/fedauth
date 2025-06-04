from django.urls import path

from fedauth.federated_oidc.views import AuthenticationRequestView

urlpatterns = [
    path('federated/<str:username>/', AuthenticationRequestView.as_view(), name='db-provider-auth'),
]
