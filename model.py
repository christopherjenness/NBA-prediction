import urllib2
from bs4 import BeautifulSoup
import pickle
import pandas as pd
import numpy

numpy.random.seed(100)

teams = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'HOU',
         'DET', 'GSW', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
         'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS',
         'TOR', 'UTA', 'WAS'
    ]

urls = ["http://www.basketball-reference.com/leagues/NBA_2017_games-october.html", 
        "http://www.basketball-reference.com/leagues/NBA_2017_games-november.html"
        ]

        
N = 30
M = 30
K = 8

def get_table(url):
    response = urllib2.urlopen(url)
    html = response.read()
    a = html.replace('<!--', "")
    b = a.replace('-->', "")
    c = pd.read_html(b)
    return c[-5]
    
def update_df(df, team1, team2, value):
    old_value = df[team2].loc[team1]
    print old_value, value
    if old_value == 0:
        new_value = float(value)
    else:
        new_value = (float(old_value) + float(value)) / 2
    df[team2].loc[team1] = new_value
    return df
    
def extract_data(table):
    team1 = table.loc[2][0]
    team2 = table.loc[3][0]
    pace = table.loc[3][1]
    team1_OR = table.loc[2][6]
    team2_OR = table.loc[3][6]
    return team1, team2, team1_OR, team2_OR, pace
    
def full_update(url, df_pace, df_OR):
    table = get_table(url)
    team1, team2, team1_OR, team2_OR, pace = extract_data(table)
    df_pace = update_df(df_pace, team1, team2, pace)
    df_pace = update_df(df_pace, team2, team1, pace)
    df_OR = update_df(df_OR, team1, team2, team1_OR)
    df_OR = update_df(df_OR, team2, team1, team2_OR)
    return df_pace, df_OR
    
def get_scores(team1, team2, predictions=predictions):
    team1s = predictions.loc[team1][team2]
    team2s = predictions.loc[team2][team1]
    print team1, team2
    print team1s, team2s
    print ''

# Get all box score urls 
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

# Get offensive rating and pace for each game
df_pace = pd.DataFrame(0, index=teams, columns=teams)
df_OR = pd.DataFrame(0, index=teams, columns=teams)
urls = pickle.load( open( "box_urls.p", "rb" ) )
for url in urls:
    url = 'http://www.basketball-reference.com' + url
    print (url)
    df_pace, df_OR = full_update(url, df_pace, df_OR)

df_pace.to_csv('pace.csv')
df_OR.to_csv('OR.csv')
R_pace = numpy.genfromtxt('pace.csv', delimiter=',', skip_header=1)[:, 1:]
R_OR = numpy.genfromtxt('OR.csv', delimiter=',', skip_header=1)[:, 1:]

# Factor pace and offensive rating matrix
P = numpy.random.rand(N,K)
Q = numpy.random.rand(M,K)
nP, nQ = matrix_factorization(R_pace, P, Q, K)
nR_pace = numpy.dot(nP, nQ.T)
nP, nQ = matrix_factorization(R_OR, P, Q, K)
nR_OR = numpy.dot(nP, nQ.T)

# Predict scores from pace and offensive rating
predictions = nR_pace * nR_OR / 100 
predictions = pd.DataFrame(predictions, index=teams, columns=teams )
predictions.to_csv('predictions.csv')

# Predict individual scores
get_scores('NYK', 'WAS')
get_scores('MIL', 'MIA')
get_scores('POR', 'TOR')
get_scores('PHI', 'MIN')
get_scores('CHI', 'UTA')

