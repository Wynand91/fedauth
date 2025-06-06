from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .oidc.jumpcloud.views import (
    JumpcloudAuthenticationRequestView,
)

urlpatterns = [
    path('admin/', include('fedauth.oidc_admin.urls')),
    path('admin/', admin.site.urls),  # just to register 'admin' namespace
    path('oidc/', include('fedauth.urls')),
    # oidc providers configured in settings
    path("jumpcloud/authenticate/", JumpcloudAuthenticationRequestView.as_view(), name="jumpcloud_authentication_init"),
    # simplejwt urls
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
