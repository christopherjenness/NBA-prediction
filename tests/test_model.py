import mock
import model.model as model


@mock.patch.object(model.NBAModel, 'write_matrices',
                   return_value=True)
def test_NBAModel(*args):
    nba_model = model.NBAModel()
    assert hasattr(nba_model, 'urls')
    assert hasattr(nba_model, 'teams')
    assert hasattr(nba_model, 'box_urls')
    assert hasattr(nba_model, 'predictions')

    nba_model = model.NBAModel(update=True)
    assert hasattr(nba_model, 'urls')
    assert hasattr(nba_model, 'teams')
    assert hasattr(nba_model, 'box_urls')
    assert hasattr(nba_model, 'predictions')


def test_prediction():
    nba_model = model.NBAModel()
    nba_model.get_scores('TOR', 'LAC')
    
