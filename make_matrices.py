import urllib2
import pandas as pd

teams = ['ATL', 'BOS', 'BRK', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'HOU',
         'DET', 'GSW', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
         'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS',
         'TOR', 'UTA', 'WAS'
    ]

def get_table(url):
    response = urllib2.urlopen(url)
    html = response.read()
    a = html.replace('<!--', "")
    b = a.replace('-->', "")
    c = pd.read_html(b)
    return c[4]
    
def update_df(df, team1, team2, value):
    old_value = df[team2].loc[team1]
    if old_value == 0:
        new_value = value
    else:
        new_value = (old_value + value) / 2
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
    

df_pace = pd.DataFrame(0, index=teams, columns=teams)
df_OR = pd.DataFrame(0, index=teams, columns=teams)

df_pace, df_OR = full_update(url, df_pace, df_OR)





