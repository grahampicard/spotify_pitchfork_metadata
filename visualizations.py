import os
os.chdir(r'C:\Users\gpicard\Desktop\Python Work\Spotify\updated_script')
import json
import seaborn as sns
import pandas as pd
from spotify_metadata import user_data
from datetime import datetime

# Credentials found by registering application at URL below 
# https://developer.spotify.com/my-applications 

credentials_json = "credentials.json"
credentials = json.load(open(credentials_json))
os.environ['SPOTIPY_CLIENT_ID'] = credentials['client_id']
os.environ['SPOTIPY_CLIENT_SECRET'] = credentials['client_secret']
os.environ['SPOTIPY_REDIRECT_URI'] = credentials['redirect_uri']

# Enter your Spotify username
graham = user_data('grahampicard') 
data = graham.all_metadata()


#Album data, labels, and formatting for graphs
album_data = data[['album','uri','release_date','score','pitchfork','album_popularity']].drop_duplicates()
album_data['album_popularity'] = album_data['album_popularity'] / 10
review = lambda x: 'Reviewed' if x == True else 'Not Reviewed'
album_data['Reviewed by Pitchfork'] = album_data['pitchfork'].map(review)
pal = {'Reviewed':(1,.2,.0), 'Not Reviewed':(.1,.95,.5)} # Spotify & PF colors


# Make Popularity KDE Graph
fig = sns.FacetGrid(album_data, hue='Reviewed by Pitchfork', palette = pal, hue_order = ['Reviewed','Not Reviewed'], size=5, aspect=4)
fig.map(sns.kdeplot, 'album_popularity',shade=True)
fig.add_legend()
fig.set_xlabels('Album Popularity on Spotify')
fig.set_ylabels('Density')
most_popular = album_data['album_popularity'].max()
fig.set(xlim=(0,9.5))
fig.savefig('popularity_kde')


# Make Release Year KDE Graph
album_data['year'] = album_data.release_date.map(lambda x: pd.to_datetime(x).year)
years = sns.FacetGrid(album_data['year'], size=4, aspect=2)
years.map(sns.kdeplot, data=album_data['year'], shade=True, color=(.1,.95,.5))
years.set(xlim=(1960,2016))
years.set_xlabels('Release Date')
years.set_ylabels('Percent')
years.savefig('release_date_kde')


# Make Heat Map of Popularity with Review Score
heat_map_data = album_data.dropna()[['album','release_date','score','album_popularity']]
heat_map_data['n'] = 1
heat_map_data['album_popularity'] = heat_map_data['album_popularity'].map(lambda x: int(x))
heat_map_data['score'] = heat_map_data['score'].map(lambda x: int(x))
pvt = heat_map_data.pivot_table(index='album_popularity', columns='score', values='n', aggfunc='sum')
pvt = pvt.fillna(0)
pvt = pvt.applymap(lambda x: int(x))
heat_map = sns.heatmap(pvt.T, linewidths=.25, cmap = 'Oranges')
heat_map.invert_yaxis()
heat_map.set_xlabel('Popularity on Spotify')
heat_map.set_ylabel('Pitchfork Review Score')