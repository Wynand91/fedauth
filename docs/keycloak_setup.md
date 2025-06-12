# Keycloak (docker required)

> Note: Docker is required to run KeyCloak locally
>- [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)
>- [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
>- [Docker Engine only (CLI-only, no GUI) - Linux](https://docs.docker.com/engine/install/)


## Step 1: Run KeyCloak container

    docker run -d --name keycloak -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:21.1.1 start-dev

 - this creates and starts a container called ‘keycloak’
 - to stop the container: `docker stop keycloak`
 - to run this container at any time: `docker start keycloak`

## Step 2: Log into admin console
 - Go to http://localhost:8080
 - Login with admin/admin
 - Create a new Realm (like your app namespace)
 - Create Users in that realm
 - Create admin Groups (e.g. admin, superuser)
   > Note: Remember these group names exactly, since they need to match settings.
 - Assign users to groups

## Step 3: Configure Client (your app)
 - Go to Clients > Create client
 - Set Client ID (your app name)
 - Set Root URL to your app URL (for redirect URIs)
 - Configure Access Type to confidential or public based on your app
 - Enable Standard Flow Enabled (for OIDC auth code flow)

## Step 4: Add Group Membership to Tokens
 - > Note: This step is a bit tricky - the [docs](shttps://www.keycloak.org/docs/latest/server_admin/index.html#assigning-permissions-using-roles-and-groups) I used don't match the dashboard exactly. 
   > If all else fails - ask chatgpt.
 - Go to Client Scopes > Create a new client scope, e.g. groups
 - Add and configure mapper
 - Now, when you authenticate, your JWT tokens will have e.g. `"groups": ["admin", "superuser"]` claim (with groups assigned to the user).

 > Note: adding scope to token is very temperamental and can be a big headache to setup. 
 > 
> If you get a Django admin error after idP login saying something like “User is authenticated but isn’t authorised to access admin”, and you know that the user belongs to the "admin" or "superuser" group,
 > Then the issue can be one of two things:
 > - The groups are probably not included in token, 
 > - The settings value for admin (`OIDC_ADMIN_GROUP`) or superuser (`OIDC_SUPER_GROUP`) config in settings.py don’t match the names of groups configured on keycloak dashboard.
 > 
 > **Extra debugging tip**: It seems that keycloak might be caching tokens, so if you make changes to token scope, then it will probably not reflect instantly.
> 
 > **Also** make sure to include the scope on your federated model config in the scopes field!
> 
> To those about to configure idP token scopes - I salute you. 🫡

## Step 5: Set up user credentials
 - In order to login via idP as a user, you need to set up credentials for the user on the KeyCloak dashboard.
 - go to users panel
 - select user that you want to create password for, and then credentials tab
 - change password

## Step 6: Test with OIDC
In your running Django app admin, go to Federated Provider model view and add a Provider with:
- domain: this is the email domain you will use for users (e.g. myapp.com)
- client id: this is the client ID of your app in KeyCloak dashboard (usually your app client name or whatever id you chose when creating the client)  - On keycloak dashboard, select ‘Clients’,  then ‘settings’ tab to find your client ID
- secret key: On KeyCloak dashboard, select ‘Clients’,  then ‘credentials’ tab to find your secret key.
- endpoints: Endpoints for KeyCloak client - Replace {realm-name} with your realm’s name:
  - Authorization endpoint: http://localhost:8080/realms/{realm-name}/protocol/openid-connect/auth
  - Token endpoint: http://localhost:8080/realms/{realm-name}/protocol/openid-connect/token
  - Usrinfo endpoint: http://localhost:8080/realms/{realm-name}/protocol/openid-connect/userinfo
  - JWKS endpoint: http://localhost:8080/realms/{realm-name}/protocol/openid-connect/certs
