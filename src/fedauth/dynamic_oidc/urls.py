from django.urls import path

from fedauth.dynamic_oidc.views import DynamicAuthenticationRequestView

urlpatterns = [
    path('federated/<str:username>/', DynamicAuthenticationRequestView.as_view(), name='fed-provider-auth'),
]
