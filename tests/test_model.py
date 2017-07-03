import mock
import numpy as np
import pandas as pd
import model.model as model

mock_stats = [[np.nan for i in range(7)],
              [np.nan for i in range(7)],
              ['CLE', 98.8, .597, 12.5, 29.3, .170, 121.4],
              ['GSW', 98.8, .589, 11.3, 31.7, .256, 130.5]]
mock_stats_df = pd.DataFrame(mock_stats, columns=range(7))


def test_NBAModel():
    nba_model = model.NBAModel()
    assert hasattr(nba_model, 'urls')
    assert hasattr(nba_model, 'teams')
    assert hasattr(nba_model, 'box_urls')
    assert hasattr(nba_model, 'predictions')


@mock.patch.object(model.NBAModel, 'write_matrices',
                   return_value=True)
@mock.patch.object(model.NBAModel, 'soft_impute',
                   return_value=True)
@mock.patch.object(model.NBAModel, 'get_stats',
                   return_value=mock_stats_df)
def test_NBAModel_update(*args):
    nba_model = model.NBAModel(update=True)
    assert hasattr(nba_model, 'urls')
    assert hasattr(nba_model, 'teams')
    assert hasattr(nba_model, 'box_urls')
    assert hasattr(nba_model, 'predictions')


def test_prediction():
    nba_model = model.NBAModel()
    nba_model.get_scores('TOR', 'LAC')
    
