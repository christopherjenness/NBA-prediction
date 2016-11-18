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
    
def matrix_factorization(R, P, Q, K, steps=5000, alpha=0.0002, beta=0.02):
    """
    Stolen from:
    http://www.quuxlabs.com/blog/2010/09/matrix-factorization-a-simple-tutorial-and-implementation-in-python/
    """
    Q = Q.T
    for step in xrange(steps):
        print step
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i,:],Q[:,j])
                    for k in xrange(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = numpy.dot(P,Q)
        e = 0
        for i in xrange(len(R)):
            for j in xrange(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - numpy.dot(P[i,:],Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * ( pow(P[i][k],2) + pow(Q[k][j],2) )
        if e < 0.001:
            break
    return P, Q.T

    
def get_scores(team1, team2, predictions):
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
get_scores('ATL', 'CHO', predictions=predictions)
get_scores('PHO', 'IND', predictions=predictions)
get_scores('DET', 'CLE', predictions=predictions)
get_scores('GSW', 'BOS', predictions=predictions)
get_scores('POR', 'NOP', predictions=predictions)
get_scores('BRK', 'OKC', predictions=predictions)
get_scores('MEM', 'DAL', predictions=predictions)
get_scores('TOR', 'DEN', predictions=predictions)
get_scores('LAC', 'SAC', predictions=predictions)
get_scores('SAS', 'LAL', predictions=predictions)

