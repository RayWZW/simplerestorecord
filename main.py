from flask import Flask, redirect, render_template, session
import json
import os
import logging
from callback import callback_blueprint 
from joinpanel import joinpanel_blueprint

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set up logging for IP addresses
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', filename='app.log', filemode='a')
logger = logging.getLogger()

# Load bot configuration
with open('bot/botconfig.json') as config_file:
    config = json.load(config_file)

CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
TOKEN = config['token']
GUILD_ID = config['guild_id']
ROLE_ID = config['role_id']
REDIRECT_URI = 'https://utcverify.loophole.site/callback'

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

@app.route('/')
def index():
    return redirect('/utcthugs')

@app.route('/utcthugs')
def utcthugs():
    oauth2_url = (
        f"https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code"
        f"&redirect_uri={REDIRECT_URI}&scope=identify+guilds.join+email+guilds+guilds.members.read&state=utcthugs"
    )
    return redirect(oauth2_url)

@app.route('/menu')
def menu():
    if 'username' in session:
        username = session['username']
        return render_template('menu.html', username=username)
    return redirect('/')

# Register the blueprints
app.register_blueprint(callback_blueprint)
app.register_blueprint(joinpanel_blueprint)

if __name__ == '__main__':
    app.run(debug=True, port=6500)
