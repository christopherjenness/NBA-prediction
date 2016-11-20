import urllib2
from bs4 import BeautifulSoup
import pickle
import pandas as pd
import subprocess

class NBAModel:
    
    def __init__(self, update=False):
            self.urls = ["http://www.basketball-reference.com/leagues/NBA_2017_games-october.html", 
                         "http://www.basketball-reference.com/leagues/NBA_2017_games-november.html"
                         ]
            self.teams = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'HOU',
                          'DET', 'GSW', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
                          'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS',
                           'TOR', 'UTA', 'WAS']
            self.box_urls = self.get_urls()
            if update:
                self.df_pace = pd.DataFrame(0, index=self.teams, columns=self.teams)
                self.df_OR = pd.DataFrame(0, index=self.teams, columns=self.teams)
                self.df_pace, self.df_OR = self.make_matrices()
                self.soft_impute()
            self.predictions = self.get_predictions()
                   
    def get_urls(self):   
        box_urls=[]
        for url in self.urls:
            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            soup.find_all('a')
            for link in soup.find_all('a'):
                if link.get('href').startswith('/boxscores/2'):
                    box_urls.append(str(link.get('href')))
        pickle.dump(box_urls, open( "box_urls.p", "wb" ) )
        return box_urls

    def get_stats(self, url):
        response = urllib2.urlopen(url)
        html = response.read()
        stat_html = html.replace('<!--', "")
        stat_html = stat_html.replace('-->', "")
        stats = pd.read_html(stat_html)
        return stats[-5]
    
    def update_df(self, df, team1, team2, value):
        old_value = df[team2].loc[team1]
        if old_value == 0:
            new_value = float(value)
        else:
            new_value = (float(old_value) + float(value)) / 2
        df[team2].loc[team1] = new_value
        return df
    
    def extract_data(self, table):
        team1 = table.loc[2][0]
        team2 = table.loc[3][0]
        pace = table.loc[3][1]
        team1_OR = table.loc[2][6]
        team2_OR = table.loc[3][6]
        return team1, team2, team1_OR, team2_OR, pace
    
    def full_update(self, url, df_pace, df_OR):
        table = self.get_stats(url)
        team1, team2, team1_OR, team2_OR, pace = self.extract_data(table)
        df_pace = self.update_df(df_pace, team1, team2, pace)
        df_pace = self.update_df(df_pace, team2, team1, pace)
        df_OR = self.update_df(df_OR, team1, team2, team1_OR)
        df_OR = self.update_df(df_OR, team2, team1, team2_OR)
        return df_pace, df_OR
        
    def make_matrices(self):
        df_pace, df_OR = self.df_pace, self.df_OR
        for url in self.box_urls:
            url = 'http://www.basketball-reference.com' + url
            df_pace, df_OR = self.full_update(url, df_pace, df_OR)
        return df_pace, df_OR
        
    def write_matrices(self):
        self.df_pace.to_csv('pace.csv')
        self.df_OR.to_csv('OR.csv')
        
    def soft_impute(self):
        subprocess.check_output(['Rscript', './predict_soft_impute.R'])
        
    def get_predictions(self):
        predictions = pd.read_csv('predictions.csv')
        predictions = predictions.set_index('Unnamed: 0')
        return predictions
        
    def get_scores(self, team1, team2):
        team1s = self.predictions.loc[team1][team2]
        team2s = self.predictions.loc[team2][team1]
        print team1, team2
        print team1s, team2s
        print ''

a = NBAModel()
a.get_scores('POR', 'BRK')
