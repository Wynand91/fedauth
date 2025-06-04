from django.contrib.auth.forms import AuthenticationForm


class UsernameForm(AuthenticationForm):
    """
    We don't want the password field for the authentication form.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field
        self.fields.pop('password')
