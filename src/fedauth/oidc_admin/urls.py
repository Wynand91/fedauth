from django.urls import path

from fedauth.oidc_admin.views import LoginView, DefaultLoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='admin-login'),
    path('login/default/<str:username>/', DefaultLoginView.as_view(template_name='admin/login.html'), name='admin-login-default'),
]
