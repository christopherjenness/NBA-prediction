import urllib2
from bs4 import BeautifulSoup
import pickle

urls = ["http://www.basketball-reference.com/leagues/NBA_2017_games-october.html", 
        "http://www.basketball-reference.com/leagues/NBA_2017_games-november.html"
        ]
box_urls=[]
for url in urls:
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    soup.find_all('a')
    for link in soup.find_all('a'):
        if link.get('href').startswith('/boxscores/2'):
            box_urls.append(str(link.get('href')))

pickle.dump(box_urls, open( "box_urls.p", "wb" ) )
