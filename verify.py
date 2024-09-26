import json
import requests
import os

# Load bot configuration
with open('bot/botconfig.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
GUILD_ID = config['guild_id']
ROLE_ID = config['role_id']

def verify_user(access_token, user_id):
    # Add user to the guild
    if add_user_to_guild(access_token, user_id, GUILD_ID):
        # Assign role to the user
        assign_role_to_user(user_id, GUILD_ID, ROLE_ID)

def add_user_to_guild(access_token, user_id, guild_id):
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}'
    data = {
        'access_token': access_token
    }
    response = requests.put(url, headers=headers, json=data)
    return response.status_code == 201

def assign_role_to_user(user_id, guild_id, role_id):
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    url = f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}/roles/{role_id}'
    response = requests.put(url, headers=headers)
    return response.status_code == 204
