from flask import Blueprint, request, redirect, session
import json
import requests
import os
from verify import verify_user  # Import the verification function

callback_blueprint = Blueprint('callback', __name__)

# Load bot configuration
with open('bot/botconfig.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
GUILD_ID = config['guild_id']
ROLE_ID = config['role_id']
REDIRECT_URI = 'https://utcverify.loophole.site/callback'

@callback_blueprint.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "No code provided", 400

    token_url = "https://discord.com/api/oauth2/token"
    data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()

    if 'access_token' in token_info:
        access_token = token_info['access_token']
        user_info = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"}).json()

        # Save user info to a JSON file and verify user
        save_user_info(user_info, access_token)

        # Call the verify_user function from verify.py
        verify_user(access_token, user_info['id'])

        # Join the user to the server
        join_user_to_server(access_token, user_info['id'])

        # Store username in session for menu
        session['username'] = user_info['username']

        return redirect('/menu')  # Redirect after successful verification
    else:
        return "Error retrieving access token", 400

def save_user_info(user_info, access_token):
    user_id = user_info['id']
    file_path = os.path.join('data', f'{user_id}.json')

    user_data = {
        'id': user_info.get('id'),
        'username': user_info.get('username'),
        'discriminator': user_info.get('discriminator'),
        'email': user_info.get('email'),
        'avatar': user_info.get('avatar'),
        'access_token': access_token
    }

    with open(file_path, 'w') as f:
        json.dump(user_data, f, indent=4)

def join_user_to_server(access_token, user_id):
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f'https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}'
    data = {
        'access_token': access_token,
        'roles': [ROLE_ID]  # Assign the role here if desired
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [201, 204]:
        print(f"Failed to add user {user_id} to server: {response.text}")
