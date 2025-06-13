from django.contrib import admin

from fedauth.forms import BaseProviderAdminForm
from fedauth.models import DynamicProvider, StaticProvider


class DynamicProviderForm(BaseProviderAdminForm):

    class Meta:
        model = DynamicProvider
        exclude = ('client_secret_cipher',)


@admin.register(DynamicProvider)
class DynamicProviderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'domain']
    list_filter = ['created_at', 'domain']
    search_fields = ['domain']
    ordering = ['domain']
    form = DynamicProviderForm
    readonly_fields = ('created_at', 'updated_at',)
    fields = (
        'created_at',
        'updated_at',
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
        # only include client secret field when new object is being created
        if not obj:
            return self.fields + self.add_fields
        return super().get_fields(request, obj)


class StaticProviderForm(BaseProviderAdminForm):

    class Meta:
        model = StaticProvider
        exclude = ('client_secret_cipher',)


@admin.register(StaticProvider)
class StaticProviderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'provider']
    list_filter = ['created_at', 'provider']
    search_fields = ['provider']
    ordering = ['provider']
    form = StaticProviderForm
    readonly_fields = ('created_at', 'updated_at',)
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
        # only include client secret field when new object is being created
        if not obj:
            return self.fields + self.add_fields
        return super().get_fields(request, obj)
