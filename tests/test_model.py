import mock
import model.model as model


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
def test_NBAModel_update(*args):
    nba_model = model.NBAModel(update=True)
    assert hasattr(nba_model, 'urls')
    assert hasattr(nba_model, 'teams')
    assert hasattr(nba_model, 'box_urls')
    assert hasattr(nba_model, 'predictions')


def test_prediction():
    nba_model = model.NBAModel()
    nba_model.get_scores('TOR', 'LAC')
    
