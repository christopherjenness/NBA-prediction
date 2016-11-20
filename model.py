"""


See readme for details.
"""

import urllib2
import pickle
import subprocess
import pandas as pd
from bs4 import BeautifulSoup

class NBAModel:
    """
    NBA model for predicting final scores.  
    Seperate predictions are made for Offensive Rating and Pace, which
        are combined to predict the final score.
    """
    def __init__(self, update=False):
        """
        Attributes:
            urls (list): list of basketball reference URLs of games to include in model
                this needs to be manually updated
            teams (list): list of team canonical abbreviations
            box_urls (list): list of URLs to box scores for games included in model
            predictions (pd.DataFrame): DataFrame of predicted score.
                Each entry is the predicted score that the team in the index will score against
                each team in the columns. To predict a game, two lookups are required, one for
                each team against the other.

        Args:
            update (bool): If True, update predictions DataFrame by rescraping and recomputing
                all values.  Otherwise, just use the cached predictions DataFrame.
        """
        self.urls = ["http://www.basketball-reference.com/leagues/NBA_2017_games-october.html",
                     "http://www.basketball-reference.com/leagues/NBA_2017_games-november.html"
                    ]
        self.teams = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'HOU',
                      'DET', 'GSW', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
                      'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS',
                      'TOR', 'UTA', 'WAS'
                     ]
        self.box_urls = self.get_urls()
        if update:
            self.df_pace = pd.DataFrame(0, index=self.teams, columns=self.teams)
            self.df_OR = pd.DataFrame(0, index=self.teams, columns=self.teams)
            self.df_pace, self.df_OR = self.make_matrices()
            self.soft_impute()
        self.predictions = self.get_predictions()

    def get_urls(self):
        """
        Gets all URLs for box scores (basketball-reference.com) from current season

        Returns:
            box_urls (list): list of box score URLs from basketball reference
        """
        box_urls = []
        for url in self.urls:
            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            soup.find_all('a')
            for link in soup.find_all('a'):
                if link.get('href').startswith('/boxscores/2'):
                    box_urls.append(str(link.get('href')))
        pickle.dump(box_urls, open("box_urls.p", "wb"))
        return box_urls

    def get_stats(self, url):
        """
        Extracts statistics from URL

        Args:
            url (str): basketball-reference.com box score UnicodeTranslateError

        Returns:
            stats (pd.DataFrame): DataFrame of statistics from game
        """
        response = urllib2.urlopen(url)
        html = response.read()
        stat_html = html.replace('<!--', "")
        stat_html = stat_html.replace('-->', "")
        stats = pd.read_html(stat_html)
        return stats[-5]

    def update_df(self, df, team1, team2, value):
        """
        Updates df to add value of team1 and team2.
        For example, you can update the pace dataframe to add a game's pace.csv

        Args:
            df (pd.DataFrame): DataFrame to update
            team1: team on x axis index to update
            team2: team on columns to update
            value: value to add to DataFrame

        Returns:
            df (pd.DataFrame): updated DataFrame
        """
        old_value = df[team2].loc[team1]
        if old_value == 0:
            new_value = float(value)
        else:
            new_value = (float(old_value) + float(value)) / 2
        df[team2].loc[team1] = new_value
        return df

    def extract_data(self, table):
        """
        Extracts pace and offensive rating data from basketball-reference tables

        Args:
            table (pd.DataFrame): table of statistics scraped from basketball-reference
                contains advanced stats for a given games.

        Returns:
            team1 (str): Abbreviation of team1
            team2 (str): Abbreviation of team2
            team1_OR (float): Offensive rating of team1 (points per 100 posessions)
            team2_OR (float): Offensive rating of team2 (points per 100 posessions)
            pace (float): pace of game (possessions per game)
        """
        team1 = table.loc[2][0]
        team2 = table.loc[3][0]
        pace = table.loc[3][1]
        team1_OR = table.loc[2][6]
        team2_OR = table.loc[3][6]
        return team1, team2, team1_OR, team2_OR, pace

    def full_update(self, url, df_pace, df_OR):
        """
        Updates the pace and offensive rating matrices for a given game.

        Args:
            url (str): URL to box score (basketball-reference.com)
            df_pace (pd.DataFrame): pace DataFrame to update
            df_OR (pd.DataFrame): Offensive Rating DataFrame to update

        Returns:
            df_pace, df_OR (pd.DataFrame, pd.DataFrame):
                updated pace and Offensive rating DataFrames
        """

        table = self.get_stats(url)
        team1, team2, team1_OR, team2_OR, pace = self.extract_data(table)
        df_pace = self.update_df(df_pace, team1, team2, pace)
        df_pace = self.update_df(df_pace, team2, team1, pace)
        df_OR = self.update_df(df_OR, team1, team2, team1_OR)
        df_OR = self.update_df(df_OR, team2, team1, team2_OR)
        return df_pace, df_OR

    def make_matrices(self):
        """
        Makes matrices of offesive rating and pace
        Each entry in the matrix is the value (offensive rating or pace)
            of team1 against team2 (rows and columns respectively) for
            all games considered in the model.
        """
        df_pace, df_OR = self.df_pace, self.df_OR
        for url in self.box_urls:
            url = 'http://www.basketball-reference.com' + url
            df_pace, df_OR = self.full_update(url, df_pace, df_OR)
        return df_pace, df_OR

    def write_matrices(self):
        """
        Writes pace and offensive ratings csv files.
        """
        self.df_pace.to_csv('pace.csv')
        self.df_OR.to_csv('OR.csv')

    def soft_impute(self):
        """
        Calls soft impute algorithm in R.
        Write predictions.csv
        """
        subprocess.check_output(['Rscript', './predict_soft_impute.R'])

    def get_predictions(self):
        """
        Loads predictions from predictions.csv

        Returns:
            predictions (pd.DataFrame): DataFrame of predictions
        """
        predictions = pd.read_csv('predictions.csv')
        predictions = predictions.set_index('Unnamed: 0')
        return predictions

    def get_scores(self, team1, team2):
        """
        Prints predicted score of two teams playing against each other.
        Teams can be in any order since home team advantage is not considered.

        Args:
            team1 (str): team1 abbreviation
            team2 (str): team2 abbreviation

        Returns:
            None: Prints score
        """
        team1s = self.predictions.loc[team1][team2]
        team2s = self.predictions.loc[team2][team1]
        print(team1, team2)
        print(team1s, team2s)
        print('')

model = NBAModel()
model.get_scores('POR', 'BRK')
