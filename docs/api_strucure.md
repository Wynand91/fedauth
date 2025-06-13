# Login endpoints

## This package provides two login endpoints:
  - `/login/` - to get idP auth url
  - `/login/token-exchange/` - to exchange the short-live code for a valid JWT token


> Note - The endpoint base will be determined by where you register the package urls on your urls.py
>
> For demo purposes, consider the following as the package url registration:
>```python
>urlpatterns = [
>    path('admin/', admin.site.urls),
>    # register fedauth auth urls (authentication, callback and logout url)
>    path('oidc/', include('fedauth.urls')),
>]
>
>```
> Meaning the full API's (registered on the `oidc/` path) will look like this:
> - `http://localhost:8000/oidc/login/`
> - `http://localhost:8000/oidc/login/token-exchange/`
> (assuming your app is running on localhost port 8000)

# `/login/` endpoint

 ## URL pramaters:
  - The login url needs to declare where user should be redirected to after login success (next) or login failure (fail) 

 ## Request body:
  - The login is a post request that requires either a 'username' (email) or a 'provider'  in 
the request data:
  - > - **'username'** (email) :
    >   - If a **username** is in request body, the API will check if the username domain is listed in the Dynamic Provider table.
    >   - If the **domain is found**, the auth url is built by API and returned to the frontend, who can then redirect to idP.
    >   - If the **domain is not found**, there will be no auth url in the response, and it is up to frontend to handle default login then (username and password) - Meaning your app should also rely on a default login
    >   - or **'provider'**:
    >     - If a **provider** is in the request body, the API will check if there is such a provider in the Static Provider table, and built the idP auth url, 
    >     - which is found in response.

# Handling the response

- The `/login/` post request, will respond with the idP auth URL (if found).
- The frontend should then redirect the user to the idP provider

# Below is a python code sample of how to call the login endpoint and how to handle response
## For dynamic login request:
* This will happen when user submits username/email*
```python
# do API call to backend
next_url = request.build_absolute_uri(reverse_lazy('home'))  # build full URL for next page
fail_url = request.build_absolute_uri(reverse_lazy('login'))  # build full URL for fail page
params = {'next': next_url, 'fail': fail_url}
# Call your backend API - with username in request data
login_url = f'http://localhost:8000/oidc/login/?{urlencode(params)}'
resp = requests.post(login_url, data={'username': username})

if resp.status_code == 200:
    data = response.json()
    auth_url = data.get('auth_url')
    if auth_url:
        return redirect(auth_url)

return redirect('login_default')  # your default login view
```
## For static login request:
* This will happen when user clicks e.g 'Log in with Google'*
```python
# do API call to backend
next_url = request.build_absolute_uri(reverse_lazy('home'))  # build full URL for next page
fail_url = request.build_absolute_uri(reverse_lazy('login'))  # build full URL for fail page
params = {'next': next_url, 'fail': fail_url}
# Call your backend API - with provider in request data
login_url = f'http://localhost:8000/oidc/login/?{urlencode(params)}'
resp = requests.post(login_url, data={'provider': 'google'})

if resp.status_code == 200:
    data = response.json()
    auth_url = data.get('auth_url')
    if auth_url:
        return redirect(auth_url)

return redirect('login_default')  # your default login view
```
# After Identity Provider authentication

- Once the frontend redirects to the auth provider authentication page and the user authenticates successfully, 
the user will be redirected back to the url that was passed as the 'next' url parameter.
- The url however will now include a `code` url paramater that the frontend should exchange for a JWT toke on the `/login/token-exchange/` endpoint
- e.g.
- ```python
  code = request.GET['code']
  token_exhange_url = 'http://localhost:8000/oidc/login/token-exchange/'
  resp = requests.post(token_exhange_url, data={'code': code})
  resp_json = resp.json()
  token = resp_json['access_token']
  refresh_token = resp_json['refresh_token']
```
