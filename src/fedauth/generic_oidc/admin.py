from django.contrib import admin

from fedauth.forms import BaseProviderAdminForm
from fedauth.generic_oidc.models import GenericProvider


class GenericProviderForm(BaseProviderAdminForm):

    class Meta:
        model = GenericProvider
        exclude = ('client_secret_cipher',)


@admin.register(GenericProvider)
class FederatedProviderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'provider']
    list_filter = ['created_at', 'provider']
    search_fields = ['provider']
    ordering = ['provider']
    form = GenericProviderForm
    readonly_fields = ('created_at',)
    fields = (
        'created_at',
        'updated_at',
        'provider',
        'auth_endpoint',
        'token_endpoint',
        'user_endpoint',
        'jwks_endpoint',
        'client_id',
        'sign_algo',
        'scopes',
    )
    add_fields = ('client_secret',)

    def get_fields(self, request, obj=None):
        if not obj:
            return self.fields + self.add_fields
        return super().get_fields(request, obj)
