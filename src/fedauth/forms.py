from django import forms


class BaseProviderAdminForm(forms.ModelForm):
    client_secret = forms.CharField(required=False)

    def save(self, commit=True):
        obj = self.instance
        secret = self.data.get('client_secret')
        if secret:
            obj.client_secret = secret
        return super().save(commit)
