from django.contrib.auth.forms import AuthenticationForm


class UsernameForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field - not needed at first for federation check.
        self.fields.pop('password')
