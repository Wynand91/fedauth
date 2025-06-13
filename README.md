# FEDAUTH

[![codecov](https://codecov.io/gh/Wynand91/fedauth/graph/badge.svg?token=2GMX7Z0ZPT)](https://codecov.io/gh/Wynand91/fedauth)

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Flow diagrams](#fedauth-oidc-flows-diagrams-)
- [IDP setup for local testing](#idp-setup-for-local-testing)
- [Admin OIDC setup](#admin-oidc-setup)
- [Frontend OIDC API setup](#frontend-oidc-api-setup)
- [Example 'settings.py'](#configuration)
- [Example 'urls.py'](#url-registration)
- [Template customization](#customizing-admin-login-template)
- [License](#license)

Requirements:
 - python 3.11+
 - django >= 4.2, < 5.0

# Overview

This package enables any Django project to support both **federated** and **generic** OIDC logins for the admin login page, and also provides APIs for frontend OIDC authentication.

It's an OpenID Connect authentication package with support for multiple identity providers, all configurable via database models and the django admin portal.

This package is built on top of [`mozilla-django-oidc`](https://mozilla-django-oidc.readthedocs.io/en/stable/).

You can find all applicable `mozilla-django-oidc` configuration options [here](https://mozilla-django-oidc.readthedocs.io/en/stable/settings.html).

![login screenshot](docs/login_example.png)

## Terminology

- **Federated OIDC**:

    Refers to login flows where the username or email domain is associated with a specific organization that uses its own OIDC Identity Provider. The package retrieves the appropriate OIDC configuration by looking up the user's domain in the database.


- **Generic OIDC**:

    Refers to non-domain-specific login options typically shown as "Login with {Provider}" (e.g., "Login with JumpCloud"). These are explicitly selected by the user and not determined based on their email domain.

## Features:

Django Admin:
- **Federated Admin OIDC login**:

    Django Admin login form accepts username (email), and is automatically redirected to Identity Provider login page if their email domain is found in the 
Federated Provider table. If not found in the table, the user is asked to submit a password (default login)


- **Generic Admin OIDC login**:

    Any generic Identity Provider Login option can be added to the django login page (e.g. "Login with Google").  Generic provider configs are stored in the
Generic Provider table.

APIs:
- **Federated OIDC login endpoint**:

    The package includes a login endpoint that can be used by any frontend agent to login based on a federate username (email) 


- **Generic OIDC login endpoint**:

    This endpoint can be used to retrieve any provider auth URL.  Generic provider configs are stored on the
Generic Provider table. By using this endpoint, any generic Identity Provider Login option can be added to the frontend 
login page (e.g. "Login with Google") without having to store any provider configurations on the individual frontends. 

# Installation
To install, run:

    pip install git+https://github.com/Wynand91/fedauth.git


# Fedauth OIDC flows diagrams: 
diagrams done with [draw.io](https://www.drawio.com/)

## A) Django Admin OIDC (Federated or Generic OIDC)

![OIDC login flow](docs/diagrams/admin_oidc_flow.png)

## A) Frontend API OIDC (Federated or Generic OIDC)

![OIDC login flow](docs/diagrams/frontend_flow.png)

# IDP setup for local testing

In order to use the package, the user needs to set up developer accounts for their preferred providers. Basically any 
provider can be used, since they all have the same flow. 

**Disclaimer**: Dashboards on these OIDC provider accounts regularly change, so it is up to the user to find documentation 
on how to set up their providers.

Below is what configurations you will need, regardless of provider, in order to use the package:
  
 - What you'll need to create the provider objects in admin:
   - Client ID
   - Client secret
   - Endpoints
     - Authentication URL
     - Token URL
     - User info URL
     - JWKS urls (or 'certs' for some providers - same thing)
     

 - Configurations that have to be done on IDP dashboard:
   - Create Users on provider dashboard
   - You need to configure "admin" and "superuser" **groups**, and then add the groups **scope** to the token payload, so that the callback 
method can assign user permissions based on the groups they belong to. This can be a tricky step that requires lots of 
debugging if not set up correctly.

### Here are a few recommended providers with setup instructions:

> Note: For easiest setup I recommend: 
>- 'KeyCloak' for federated user login
>- 'Google' for non generic user login ('Login with google')

**KeyCloak** (*Easiest to set up*): [KeyCloak setup](docs/keycloak_setup.md)
- Runs locally using docker (required).
- Offers federated user functionality, and groups scope setup

**Okta** (*More complex to set up*): [
Okta setup](docs/okta_setup.md)
- Okta developer account requires a domain email address (can't use '@gmail.com' or '@yahoo.com' email)
- Offers federated user functionality, and groups scope setup

**Google** (*Relatively simple setup*): [Google setup](docs/google_setup.md)
- Use this for generic sign in setup ('Sign in with google') - N
- Offers federated user functionality, and groups scope setup

> ## Note: Handling idP sessions
> 
> Once you've authenticated a user via idP, your browser will have an open session with the idP client 
> (like when being logged in to your gmail account - the browser will always use the logged in session to authenticate when you select "log in with Google" on any service.)
> 
> This Means that if you log out of the admin, the idP session persists, and if you submit your email again, you will be logged 
> in instantly, since there is open a session. But when another user submits an email, it will just log in the first user.
> 
> You have two options to work around this when testing different users:
> 1. On KeyCloak dahsboard, go to 'sessions' panel, and close the session of the user.
> 2. Or use Incognito window for every different user.


# Admin OIDC setup

- Federated login
  - When using this package, the admin login form will only ask for a username (email)
  - When the username is submitted, the backend will check the email domain, and redirect the user to the auth provider if the 
domain is found in the FederatedProvider table.
  - If domain is not found, the admin will show a login from including a password field to handle default login.
  - see this doc for instructions: [Federated admin login](docs/federated_admin.md)

- Generic login
  - You also have the option of adding a e.g. 'Login with Google' option
  - see this doc for instructions: [Generic admin login](docs/generic_admin.md)


# Frontend OIDC API setup

- This package provides two login endpoints:
  - `/login/` - to get idP auth url
  - `/login/token-exchange/` - to exchange the short-live code for a valid JWT token

- See this doc for usage: [Fronted OIDC API](docs/api_strucure.md)
 
# Configuration

 - This package requires some configurations on your `settings.py` file
 - See example: [example settings](docs/settings_example.md)

# URL registration

- Below is an example of how to register fedauth urls
```python
urlpatterns = [
    # include fedauth admin urls before standard admin
    path('admin/', include('fedauth.oidc_admin.urls')),
    path('admin/', admin.site.urls),
    # register fedauth auth urls (authentication, callback and logout url)
    path('oidc/', include('fedauth.urls')),
    # include any generic oidc providers if using any
    path('google/authenticate/', GoogleAuthRequestView.as_view(), name="google_authentication_init",),
    path('', include(api_urls)),
]
```

## Customizing Admin login template:
- This package has a default login template called `admin/oidc_login.html`
- To customize this template (if specific styling is required, or to add non-federated login links), a custom login template can be created that either 
extends the custom template or completely overrides it.
- If a custom template is created, add the following setting to settings file: `LOGIN_TEMPLATE = '<template>'`
- NOTE: **username** should be the ONLY form field on template.



## License

This project is **not open source** (yet).

It is shared under a proprietary license for educational and portfolio purposes only.

View-only rights are granted. **No reuse, distribution, or commercial use is permitted.**  
See the LICENSE file for full terms.