# Generic Admin login
- This package provides a model (**GenericProvider**) that stores credentials for OIDC auth providers.
- This is for the **"log in with ..."** options on admin login form. In our example we will use google.


# Creating the model object:
   1. Navigate to Generic Provider in admin -> Add new.
   2. `provider` field is the provider name. (e.g. 'google')
   3. `client_id`, `client_secret` can be retrieved from OIDC provider client dashboard
   4. the `<api>_endpoint` fields will be specific to provider (see provider setup section for endpoints)
   5. `scopes`: These are the scopes that should be included for the token (scopes configured on OIDC app dashboard), e.g. `"openid profile email phone"`
   > Once a GenericProvider object is saved, OIDC redirection will automatically happen when clicking 'Login with ...' button on admin login form (if template is setup correctly - see below steps)

# Creating a Generic provider option

- The package provides a base view that can be used to create any Generic Provider view
- This view can be imported with: `from fedauth.generic_oidc.views import GenericAuthenticationRequestView`
- Create a generic view as such:
  ```python
   # src/project/custom_oidc/views
     
  from fedauth.generic_oidc.views import GenericAuthenticationRequestView
     
  class GoogleAuthRequestView(GenericAuthenticationRequestView):
      def __init__(self):
          self.alias = 'google'
          super().__init__()
  ```
   >   Note: the `self.alias` value should match the **'provider'** field on the model.

- Register google auth url view in urlpatterns
  - ```python
    # src/project/project_oidc/urls
    from django.urls import path
   
    urlpatterns = [
        path(
            "google/authenticate/",
            GoogleAuthRequestView.as_view(),
            name="google_authentication_init",
        )
    ]
    ```
    
# Template
- In order for link to appear on the Admin login page, you'll need to create a custom admin login template.
- This can either be an extension of the default template (`admin/oidc_login.html`), or an entirely new template 
- If a custom template is created, add the following setting to settings file: `LOGIN_TEMPLATE = '<template path>'`
- NOTE: **username** should be the ONLY form field on template.
- Add the link on your custom template:
 ```html
<a href="{% url 'google_authentication_init' %}" class="google-btn">
    <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" class="google-icon">
    <span>Sign in with Google</span>
</a>
```

> Note: Make sure all applicable settings are configured in settings.py file (see `Configuration` section in readme.)