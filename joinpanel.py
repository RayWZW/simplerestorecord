from flask import Blueprint, render_template, request, jsonify, redirect
import json
import os
import requests

joinpanel_blueprint = Blueprint('joinpanel', __name__)

with open('bot/botconfig.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']

@joinpanel_blueprint.route('/joinpanel', methods=['GET', 'POST'])
def joinpanel():
    if request.method == 'POST':
        selected_guild_id = request.form['guild_id']
        selected_role_id = request.form['role_id']
        join_all_users(selected_guild_id, selected_role_id)
        return redirect('/joinpanel')

    guilds = get_bot_guilds()
    return render_template('joinpanel.html', guilds=guilds)

@joinpanel_blueprint.route('/roles/<guild_id>', methods=['GET'])
def get_roles(guild_id):
    headers = {
        'Authorization': f'Bot {TOKEN}',
    }
    response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/roles', headers=headers)
    roles = response.json() if response.status_code == 200 else []
    return jsonify(roles)

def get_bot_guilds():
    headers = {
        'Authorization': f'Bot {TOKEN}',
    }
    response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=headers)
    return response.json() if response.status_code == 200 else []

def join_all_users(guild_id, role_id):
    user_files = os.listdir('data')
    for user_file in user_files:
        if user_file.endswith('.json'):
            user_data_path = os.path.join('data', user_file)
            with open(user_data_path, 'r') as f:
                user_data = json.load(f)
                access_token = user_data.get('access_token')
                if access_token:
                    add_user_to_guild(access_token, user_data['id'], guild_id, role_id)

def add_user_to_guild(access_token, user_id, guild_id, role_id):
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    
    member_url = f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}'
    member_response = requests.get(member_url, headers=headers)

    if member_response.status_code == 200:
        current_roles = member_response.json().get('roles', [])
        if role_id not in current_roles:
            current_roles.append(role_id)
            data = {'roles': current_roles}
            requests.patch(member_url, headers=headers, json=data)
    elif member_response.status_code == 404:
        url = f'https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}'
        data = {
            'access_token': access_token,
            'roles': [role_id]
        }
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 201

    return False
