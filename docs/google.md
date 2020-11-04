# Google Authentication 

## Creating your google app
1. login into the [Google Developers Console](https://console.developers.google.com/), go to the Dashboard and create a **New Project**
1. Name your project, users will se this name while logging in, so use something reasonable.
1. Click "Create"

![create app](img/google_0.png?raw=true)
1. Go to "Credentials" on the left panel, click "Create Credentials", and choose "OAuth Client ID" from the dropdown 
![create app](img/google_1.png?raw=true)
1. under **Authorized Java Script origins**, add your site url (e.g. `http://localhost:8000/`)
1. under **Authorized redirect URIs** add `http://yoursiteurl.com/accounts/google/login/callback/`

![create app](img/google_2.png?raw=true)
1. Note your client ID, and client Secret and set the respective environment variables: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

The app will automatically detect this environment variables and set the authentication for you.

We use [Django AllAuth](https://django-allauth.readthedocs.io/en/latest/) Library, so feel free to extend and or configure any other provider.