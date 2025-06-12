# Federated Admin login

 - This package provides a model (**FederatedProvider**) that stores credentials for OIDC auth providers.
 - The admin login page will require the user to submit a username (email). Upon submission of this email, a 
lookup will happen to check if email domain should be redirected to the external OIDC provider authentication screen.
 - If the email domain is not defined on the model, the user will be asked to submit their password, and will log in with
default django authentication.

# Creating the model object:
   1. Navigate to Generic Provider in admin -> Add new.
   2. `domain` field is the (drumroll....) domain. (e.g. 'johnspizza.com')
   3. `client_id`, `client_secret` can be retrieved from OIDC provider client dashboard
   4. the `<api>_endpoint` fields will be specific to provider (see provider setup section for endpoints)
   5. `scopes`: These are the scopes that should be included for the token (scopes configured on OIDC app dashboard), e.g. `"openid profile email phone groups""`
>Once a FederatedProvider object is save, OIDC redirection will automatically happen when submitting a username on admin login form (ensure settings.py is configured - see example)

> Note: Make sure all applicable settings are configured in settings.py file (see `Configuration` section in readme.)