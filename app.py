"""
Example of using Discord OAuth to allow someone to
log in to your site. The scope of 'email+identify' only
lets you see their email address and basic user id.
"""
from requests_oauthlib import OAuth2Session
import getpass
from flask import Flask, request, redirect, session, render_template
import os

# Disable SSL requirement
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
client_id = r'123445678' # Get from https://discordapp.com/developers/applications
client_secret = getpass.getpass()
redirect_uri='http://127.0.0.1:5000/discord_oauth'
scope = ['identify', 'email']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def home():
    """
    Presents the 'Login with Discord' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['oauth_state'] = state
    print(session['oauth_state'])
    print("Login url: %s" % login_url)
    
    
    return '<a href="' + login_url + '">Login with Discord</a>'

@app.route("/discord_oauth")
def discord_oauth():
    

    """
    The callback we specified in our app.
    Processes the code given to us by Discord and sends it back
    to Discord requesting a temporary access token so we can 
    make requests on behalf (as if we were) the user.
    e.g. https://discordapp.com/api/users/@me
    The token is stored in a session variable, so it can
    be reused across separate web requests.
    """
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['oauth_state'], scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    
    session['discord_token'] = token
    print(session['discord_token'])

    '''
    {'access_token': 'I41EKBphFc8G2xsdTR######', 'expires_in': 604800, 
    'refresh_token': 'GsIQzda0RPw5#####, 'scope': ['identify', 'email'], 
    'token_type': 'Bearer', 'expires_at': 1585440920.5932162}
    '''

    return 'Thanks for granting us authorization. We are logging you in! You can now visit <a href="/profile">/profile</a>'


@app.route("/profile")
def profile():
    """
    Example profile page to demonstrate how to pull the user information
    once we have a valid access token after all OAuth negotiation.
    """
    discord = OAuth2Session(client_id, token=session['discord_token'])
    response = discord.get(base_discord_api_url + '/users/@me')
    print(response.json())

    '''
    {'id': '########', 'username': '######', 'avatar': None, 'discriminator': '####', 
    'email': '######@yahoo.com', 'verified': True, 'locale': 'en-US', 
    'mfa_enabled': False, 'flags': 0}
    '''

    # https://discordapp.com/developers/docs/resources/user#user-object-user-structure
    return 'Profile: %s' % response.json()['id']


# Or run like this
# FLASK_APP=discord_oauth_login_server.py flask run -h 0.0.0.0 -p 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)