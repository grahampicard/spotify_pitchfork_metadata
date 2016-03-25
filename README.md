# spotify_pitchfork_metadata
Use Spotify's API "Spotipy" and a quick and dirty Pitchfork Scraper to get your music metadata

It's not elegant, but it's functional. The documents in this repository are meant to help you set up a pandas DataFrame with:
  * Your Spotify Metadata
  * Pitchfork review scores for all albums which have existing reviews

The function in pitchfork_search.py stands alone, and it can be imported without any file dependencies. 

If you're using "spotify_metadata.py", know that it imports the pitchfork search function from the "pitchfork_search.py" script. Place it in the same directory as "spotify_metadata" to make it functional.

I've included an example file should help you get your data quickly after registering your credentials through Spotify's API.

If you find this useful, I'd love to see any work or analyses.

Enjoy!
