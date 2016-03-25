import re, requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def search(artist, album):
	""" See if an album review exists for an Artist and Album """
	#Search PF website for possible matches 
	clean = lambda x:  re.sub('[^A-Za-z0-9\s]+', ' ', x)
	query = re.sub('\s+','%20',clean(artist)+'%20'+clean(album))
	query_stem = 'http://pitchfork.com/search/?query='
	search = requests.get(query_stem + query, headers = {'user-agent':'grahampicard'})
	search_soup = BeautifulSoup(search.text, 'html.parser')

	# Find URL for Album Reviews
	if len(search_soup.findAll(class_="album-link")) == 1:
		match_url = search_soup.findAll(class_="album-link")[0]['href'] 

	# Find URL for top match if there are multiple matches
	elif len(search_soup.findAll(class_="album-link")) > 1:
		matches = [x.h1.next for x in search_soup.findAll(class_="album-link")]
		top_match = difflib.get_close_matches(album, matches, cutoff=0.1)[0]
		match_index = matches.index(top_match)
		match_url = search_soup.findAll(class_="album-link")[match_index]['href']

	else:
		print(album +" by " + artist + " not found.")
		return

	#If a score exists, 
	full_url = urljoin('http://pitchfork.com/', match_url)
	review = requests.get(full_url,headers={'user-agent':'grahampicard'})
	review_soup = BeautifulSoup(review.text, 'html.parser')

	# find scores
	int_score = lambda x: float(x.strip())

	if review_soup.find(class_='review-multi') is None:
		score = int_score(review_soup.find(class_='score').text)

	else:
		titles = [title.get_text() for title in review_soup.find(class_='review-meta').find_all('h2')]

		try:
			match = difflib.get_close_matches(album, titles, cutoff=0.1)[0]
			score = review_soup.find('h2', text=matched).parent.find(class_='score').text
			score = get_score(score)

		except IndexError:
			raise IndexError(album + ' by ' + artist + ' not found')

	return score