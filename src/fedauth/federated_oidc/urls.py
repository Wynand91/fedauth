from django.urls import path

from fedauth.federated_oidc.views import FederatedAuthenticationRequestView

urlpatterns = [
    path('federated/<str:username>/', FederatedAuthenticationRequestView.as_view(), name='fed-provider-auth'),
]
