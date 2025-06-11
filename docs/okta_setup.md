# OIDC developer setup for local testing:

> **_NOTE_** <br/>
>- While identity providers of your choice can be used, this ReadMe uses Okta for demonstration purposes.
>If another provider is used, it is up to the developer to do provider setup. 
>- These steps are subject to change on Okta's dashboard, so while there might be small differences, the general idea stays the same.

## 1. Creating OIDC provider app

Setting up Okta developer account:

1. Sign up for a developer account [here](https://developer.okta.com/signup/) (Organisation email required).
2. From your Okta Dashboard, navigate to 'Applications' -> Applications from the navigation menu.
3. Click on _Create App Integration_.
4. For the sign-in method, choose _OIDC_. The application type is a _Web Application_.
5. On the General Settings page:
   1. Choose a suitable name
   2. The grant type should be _Client Credentials_ & _Authorization Code_. The _Authorization Code_ is always enabled.
   3. Click save.
6. You will also require a few urls later (auth, token, user and jwks endpoint), 
these will look as follows (your domain can be found in the dropdown menu under username in top right corner, once logged into developer account, e.g https://dev-28035502.okta.com):
   - auth_endpoint: <https://your.domain.com/oauth2/v1/authorize/>
   - token_endpoint: <https://your.domain.com/oauth2/v1/token/>
   - user_endpoint: <https://your.domain.com/oauth2/v1/userinfo/>
   - jwks_endpoint: <https://your.domain.com/oauth2/v1/keys/>

## 2. Assigning Admin and Super-Users with OIDC (These are used to create/update app users with correct permissions via OIDC login)

- ### 2.1 Creating OKTA groups
    > **_NOTE_** <br/>
    Okta groups can be created by navigating to Directory -> Groups form the dashboard.

  1. Ensure Federation Broker Mode is **DISABLED** on the Okta application dashboard.
  2. Create a group for admins, and assign the relevant users on OKTA dashboard. Assign group to app.
  3. Create a group for superusers, and assign the relevant users on OKTA dashboard. Assign group to app.
     - These groups should be configured in project settings file as such (**!NB!**: ensure names match the exact names of groups created on okta dashboard to avoid hours of debugging):
       - ```OIDC_ADMIN_GROUP='<name of admin group>'```
       - ```OIDC_SUPER_GROUP='<name of super group>'```

- ### 2.2 Adding groups to token
  1. From the application dashboard, navigate to the _Sign On_ tab.
     1. Scroll to the _OpenID Connect ID Token_ section.
     2. Click _Edit_.
     3.  Set the _Group claim type_ to __Filter__, and the _Group claim filter_ to __groups__, __Matches regex__, "__.\*__" - do not include the quotes.
  2. From the Dashboard, navigate to Security -> API. Select the default server.
  3. Select the _Claims_ tabs.
  4. Click _Add Claim_.
  5. On the dialog:
     1. Give the claim the name __groups__.
     2. Set 'Include in token type' to __ID Tokens__, and select the __Userinfo / id_token request__ option.
     3. Value type should be __Groups__.
     4. Filter should match the regex "__.\*__".
     5. Allow in any scope.
  6. Create a "__group__" scope on OKTA dashboard. **NOTE**, this scope should be included in the `OIDC_RP_SCOPES` setting for provider.
  7. Tokens should now contain the user's assigned groups.