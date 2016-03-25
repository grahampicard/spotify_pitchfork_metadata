import spotipy, json, os, re
import numpy as np
import pandas as pd 
from time import sleep
from spotipy import util
from pitchfork_search import search

class user_data:
	# This class extracts info from the 'Spotipy' object into a pd DF
	def __init__(self, username):
		scope = 'playlist-read-private'
		token = util.prompt_for_user_token(username, scope)
		self.sp = spotipy.Spotify(auth = token)
		self.username = username

	# Navigates JSON to find album metadata from 'Spotipy' object
	def parse_tracks(self, playlist, name):
		parsed_data = []	
					   
		for item in range(len(playlist)):
			artist = playlist[item]['track']['artists'][0]['name']
			album = playlist[item]['track']['album']['name']
			uri = playlist[item]['track']['album']['uri']
			track = playlist[item]['track']['name']
			pop = playlist[item]['track']['popularity']

			#no duplicates in same playlist allowed
			if {'artist': artist, 'album': album, 'track': track} not in parsed_data:
				parsed_data.append({'artist': artist, 'album': album,
									'track': track,
							 		'playlist': name,
							 		'popularity': pop,
							 		'uri': uri})
		return parsed_data

	# Gathers track information from 'saved data' tracks of a user
	def saved_data_dump(self):
		""" Spotify's saved data is accessed by a different method than its playlist
			data.  Use this function to access saved tracks """
		run = True
		offset = 0 # you can only pull 50 a time, we'll update offset
		flat_saved_data = []

		while run is True:
			save_tracks = self.sp.current_user_saved_tracks(limit = 50, 
						  offset = offset)['items']
			
			# parse tracks and append data
			song_data = self.parse_tracks(save_tracks, 'Saved Data')
			flat_saved_data.extend(song_data)

			# stop loop if we've got all the tracks
			run = False if len(save_tracks) < 50 else True
			offset += 50

		return flat_saved_data

	# Gathers track information from 'playlists' of a user
	def playlist_data_dump(self):
		#gather playlists and IDs in a dictionary
		playlists = self.sp.user_playlists(self.username)['items']
		ids = {playlists[count]['name']: playlists[count]['id'] for count in 
			   range(len(playlists)) if playlists[count]['owner']['id'] 
			   == self.username}

		flat_playlist_data = []

		for key in ids.keys():
			try:
				current_data = self.sp.user_playlist(self.username,playlist_id = ids[key])['tracks']['items']
				flat_playlist_data.extend(self.parse_tracks(current_data, key))
			except:
				print(key + " Unsuccessful")
				pass

		return flat_playlist_data

	# Get 'playlist' and 'saved' data
	def spotify_cleaned(self):
		""" returns all of the saved songs """	
		saved = self.saved_data_dump()
		playlist = self.playlist_data_dump()
		return pd.DataFrame(saved + playlist)

	# Get metadata about albums from 'Spotipy' and from Pitchfork site
	def all_metadata(self):
		""" compile all metadata """
		user_df = self.spotify_cleaned()

		#regex to remove text like "[Collector's Edition]", "(Special)" from album
		f = lambda x: re.sub(r'(\([^)]*\))|(\[[^)]*\])','',x).strip()

		#prepare data for search
		metadata = user_df[['album', 'artist','uri']].drop_duplicates()	
		metadata['album_cleaned'] = metadata['album'].map(f)
		metadata = metadata[['album_cleaned','artist','uri']].to_dict()
		metadata['score'] = {}
		metadata['release_date'] = {}
		metadata['album_popularity'] = {}

		for key in metadata['artist'].keys():
			current_artist = metadata['artist'][key]
			current_album = metadata['album_cleaned'][key]
			uri = metadata['uri'][key]

			# get pitchfork score
			try:
				current_result = search(current_artist, current_album)
				metadata['score'][key] = current_result
				sleep(2)
			except:
				pass

			# get spotify release date
			try:
				metadata['release_date'][key] = self.sp.album(uri)['release_date']
				metadata['album_popularity'][key] = self.sp.album(uri)['popularity']
			except:
				pass

		album_metadata_df = pd.DataFrame(metadata)
		album_metadata_df.release_date = pd.to_datetime(album_metadata_df.release_date)
		album_metadata_df['pitchfork'] = np.where(np.isnan(album_metadata_df.score), False, True)
		user_df = user_df.merge(album_metadata_df, on=['uri','artist'])

		return user_df