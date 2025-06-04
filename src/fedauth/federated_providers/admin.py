from django.contrib import admin

from fedauth.federated_providers.models import FederatedProvider
from fedauth.forms import BaseProviderAdminForm


class FederatedProviderForm(BaseProviderAdminForm):

    class Meta:
        model = FederatedProvider
        exclude = ('client_secret_cipher',)


@admin.register(FederatedProvider)
class FederatedProviderAdmin(admin.ModelAdmin):
    list_display = ['created', 'domain']
    list_filter = ['created', 'domain']
    search_fields = ['domain']
    ordering = ['domain']
    form = FederatedProviderForm
    readonly_fields = ('created',)
    fields = (
        'created',
        'domain',
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
