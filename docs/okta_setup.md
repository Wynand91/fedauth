# Okta setup:

> **_NOTE_** <br/>
> 
>To create an Okta Developer account, you must use a valid business or organizational email address. Personal email 
> providers such as Gmail, Yahoo, or Outlook are not accepted during registration.

## Step 1: Creating OIDC provider app

 - Sign up for an Okta developer account [here](https://developer.okta.com/signup/)
 - On the dashboard, go to 'Applications' -> Applications. 
 - Click on *'Create App Integration'*.
 - For the sign-in method, choose *'OIDC'*. And for application type, select *'Web Application'*.
 - On 'General Settings' page:
   - Choose a name
   - The grant type should be *'Client Credentials'* & *'Authorization Code'*. The *'Authorization Code'* should be always enabled.
   - Click Save.
 - Here are the endpoints needed for the Dynamic/Static Provider model. 
   - Your **domain** can be found in the dropdown menu under username in top right corner, e.g `https://dev-28035502.okta.com`):
   - auth_endpoint: <https://your.domain.com/oauth2/v1/authorize/>
   - token_endpoint: <https://your.domain.com/oauth2/v1/token/>
   - user_endpoint: <https://your.domain.com/oauth2/v1/userinfo/>
   - jwks_endpoint: <https://your.domain.com/oauth2/v1/keys/>

## Step 2: Assigning groups with OIDC and adding groups scope to tokens.

- ### 2.1 Create groups
    - Navigate to 'Directory' -> 'Groups' form.
    - Ensure Federation Broker Mode is **DISABLED** on the Okta application dashboard.
    - Create a group for admins, 
      - Assign the relevant users to group on OKTA dashboard. 
      - Also assign group to app.
    - Create a group for superusers 
      - Assign the relevant users to group on OKTA dashboard. 
      - Also assign group to app.
    - These groups should be configured in project settings file as such:
      > - **!NB!**: ensure names match the exact names of groups created on okta dashboard to avoid hours of debugging  
      - ```OIDC_ADMIN_GROUP='<name of admin group>'```
      - ```OIDC_SUPER_GROUP='<name of super group>'```

- ### 2.2 Add groups to token
  - From the application dashboard, navigate to the *'Sign On'* tab.
     - Scroll to the *'OpenID Connect ID Token'* section
     - Click *'Edit'*
     - Set *'Group claim type'* to **'Filter'**, and the *'Group claim filter'* to **'groups'**, **'Matches regex'**, "__.\*__" - (do **NOT** include the quotes, just .*)
  - From the Dashboard, go to 'Security' -> 'API'. Select the default server.
  - Select the *'Claims'* tab.
  - Click *'Add Claim'*.
  - On the popup:
     - Give the claim the name **'groups'**.
     - Set *'Include in token type'* to **'ID Tokens'**, and select the **'Userinfo / id_token request'** option.
     - Value type should be **'Groups'**.
     - Filter should match the regex "__.\*__". (do **NOT** include the quotes, just .*)
     - Allow in any scope.
  - Create a **'group'** scope on dashboard. 
    > **NOTE**, this scope should be included in the `scopes` field for provider object.
  - Tokens should now contain the user's assigned groups.