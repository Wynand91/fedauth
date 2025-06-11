from typing import Union
from urllib.parse import urlencode

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.crypto import get_random_string
from mozilla_django_oidc.utils import (
    absolutify,
    add_state_and_verifier_and_nonce_to_session,
)
from mozilla_django_oidc.views import get_next_url

from fedauth.models import FederatedProvider, GenericProvider
from fedauth.utils import get_non_federated_provider_settings, get_federated_provider_settings


def get_settings(req, attr, *args):
    domain = req.session.get('domain')
    provider = req.session.get('provider')
    if domain:
        return get_federated_provider_settings(attr, domain, *args)
    return get_non_federated_provider_settings(attr, provider, *args)


def build_oidc_auth_url(request, provider: Union[FederatedProvider, str]):
    # throughout this method we populate the session with values that is needed later in the flow (e.g. during callback)
    request.session['next'] = get_next_url(request, 'next')
    request.session['fail'] = get_next_url(request, 'fail')

    # store values in session, so that we have context during callback
    if isinstance(provider, FederatedProvider):
        request.session['domain'] = provider.domain
    elif isinstance(provider, GenericProvider):
        request.session['provider'] = provider.provider
    else:
        raise ImproperlyConfigured('Invalid provider')

    # get credentials from provider object
    oidc_op_auth_endpoint = provider.auth_endpoint
    oidc_rp_client_id = provider.client_id

    callback_url = get_settings(request, 'OIDC_AUTHENTICATION_CALLBACK_URL', 'oidc_authentication_callback')

    # In order to easily keep track of session during the flow, we can use the session key as state parameter!
    # since the state will persist through the entire flow (during callback etc), we can easily find session later down the line.
    request.session.save()  # But we first need to save the session to generate the session id.
    state_param = request.session.session_key

    params = {
        'response_type': 'code',
        'scope': get_settings(request, 'OIDC_RP_SCOPES', 'openid email'),
        'client_id': oidc_rp_client_id,
        'redirect_uri': absolutify(request, reverse(callback_url)),
        'state': state_param,
    }

    nonce = get_random_string(get_settings(request, 'OIDC_NONCE_SIZE', 32))
    params['nonce'] = nonce

    add_state_and_verifier_and_nonce_to_session(
        request, state_param, params, None
    )
    idp_auth_url = f'{oidc_op_auth_endpoint}?{urlencode(params)}'
    return idp_auth_url
