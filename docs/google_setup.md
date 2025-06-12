# Google developer account

> Note: 
> - Google developer idP can't be user for Federated login, since '@gmail.com' can't be use as a federated domain. 
> So we can use Google for Generic Provider options - i.e. The "login with Google" option on the login form
> - that Generic Providers also shouldn't have 'groups' scope, since these idP users can't belong to a 
> "organization" where you would have groups and permissions

## Step 1: Create a Google Developer Project
 - Go to: https://console.developers.google.com/
 - Sign in with your Google account.
 - Click “Select a project” (top bar), then click “New Project”.
 - Give it a name like 'My Django App'.
 - Click Create.


## Step 2: Enable the OAuth Consent Screen
 - In the left sidebar: go to OAuth consent screen.
 - Choose "External" (unless you're only testing within your organization).
 - Fill in:
	 - App name
	 - User support email
	 - Developer contact email
 - Click Save and Continue through scopes (leave default for now).


## Step 4: Create OAuth 2.0 Credentials 
 - Go to the Google Cloud Console: https://console.cloud.google.com/
 - Select your project (top navbar) if not yet selected
 - In the left sidebar, go to: APIs & Services → Credentials
 - Now you should see the "Credentials" dashboard.
 - Click “Create Credentials +” → “OAuth client ID”
 - Select Web application
 - Add Authorized redirect URIs, e.g.: http://localhost:8000/oidc/callback/ 
 - Click Create — Google will show you your:
	- Client ID
	- Client Secret
	**Save these somewhere safe** — you’ll need them in a bit (or if you have your Django project running, 
   you can open the Admin, go to “Generic Providers”). And copy these fields into the client id and client secret fields. (See next step)

## Step 5: Add config in Django app.
 - With you Django app running, navigate to admin > Generic Providers
 - Give your provider a name, e.g. ‘google’.
 - Add the following values:
   - client id = your-google-client-id
   - client secret = your-google-client-secret
   - auth endpoint = https://accounts.google.com/o/oauth2/v2/auth
   - token endpoint = https://oauth2.googleapis.com/token
   - user endpoint = https://openidconnect.googleapis.com/v1/userinfo
   - jwks endpoint = https://www.googleapis.com/oauth2/v3/certs
 - Save.