from tests.project.settings import INSTALLED_APPS

```python
# add fedauth to installed apps
INSTALLED_APPS = [
    # default django apps
    'project',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # project apps
    # ...
    # ...
    # ...
    # auth package
    'fedauth',
]

# fedauth settings
AUTHENTICATION_BACKENDS = [
    # default authentication backends first
    "django.contrib.auth.backends.ModelBackend",
    # then fedauth backend
    "fedauth.backends.OIDCAuthenticationBackend",

]

LOGIN_TEMPLATE = 'admin/custom_login.html'  # if you are using a custom template for static OIDC login options, else this can be omitted.

# for authentication backend to know where to redirect admin after authentication. Change as per project requirements.
LOGIN_REDIRECT_URL = '/admin/'
LOGIN_REDIRECT_URL_FAILURE = '/admin/'

# mozilla-django-oidc packages uses this setting to find the callback endpoint/view.
# This value should be the name of the default callback url path. Update if implementing a custom callback.
OIDC_AUTHENTICATION_CALLBACK_URL = 'oidc-provider-callback'

# the groups created on OIDC app dashboard (ensure spelling is the same as group name on oidc app config)
OIDC_ADMIN_GROUP = 'admins'
OIDC_SUPER_GROUP = 'superusers'

# whitelist hosts for internal and frontend redirects
OIDC_REDIRECT_ALLOWED_HOSTS = os.getenv('OIDC_REDIRECT_ALLOWED_HOSTS', ['localhost', '127.0.0.1', 'localhost:8001'])  # add your frontend urls
OIDC_REDIRECT_REQUIRE_HTTPS = os.getenv('OIDC_REDIRECT_REQUIRE_HTTPS', True)  # NOTE - set this to false during testing

OIDC_SL_CODE_TIMEOUT = os.getenv('OIDC_SL_CODE_TIMEOUT', 60)  # lifetime of short-lived code used for token exchange
```

This package also requires redis to be set up
See below example of redis cache setup
```python
# setup cache and session cache
REDIS_URL = os.getenv('REDIS_URL', default='redis://localhost:6379/')
REDIS_CACHE_URL = os.getenv('REDIS_CACHE_URL', default=REDIS_URL + '0')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'  # cache alias name
```

The package uses pyjwt for token generation:
```python
ACCESS_TOKEN_LIFETIME = os.getenv('ACCESS_TOKEN_LIFETIME', default=30)
REFRESH_TOKEN_LIFETIME = os.getenv('REFRESH_TOKEN_LIFETIME', default=1)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=REFRESH_TOKEN_LIFETIME),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```