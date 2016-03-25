# Credentials found by registering application at URL below 
# https://developer.spotify.com/my-applications 

# Put creds in json format to access using these environmental variables
# located in the same directory

# Also, place 'spotify_metadata.py' and 'pitchfork_search.py' in the same
# directory to access using this process below.

import os, json
import seaborn as sns
import pandas as pd
from spotify_metadata import user_data
from datetime import datetime

credentials_json = "credentials.json"
credentials = json.load(open(credentials_json))
os.environ['SPOTIPY_CLIENT_ID'] = credentials['client_id']
os.environ['SPOTIPY_CLIENT_SECRET'] = credentials['client_secret']
os.environ['SPOTIPY_REDIRECT_URI'] = credentials['redirect_uri']

username = 'enter your username here'