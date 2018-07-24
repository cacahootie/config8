
import pytest

from config8.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_path_based():
    result = client().get('/test_data/simple/overlay.json').get_json()
    assert isinstance(result, dict)
    assert 'a' in result
    assert result['names']['thor'] == 'mythological'

def test_path_jref():
    result = client().get(
        '/test_data/simple/overlay.json?jref=names').get_json()
    assert isinstance(result, dict)
    assert result['thor'] == 'mythological'

def test_path_jref_nested_list():
    result = client().get(
        '/test_data/simple/overlay.json?jref=b.2').get_json()
    assert result == "item3"

def test_path_jref_nested_dict():
    result = client().get(
        '/test_data/simple/overlay.json?jref=d.2').get_json()
    assert result == "two"

def test_jref_nested():
    result = client().post('/jsonreference',
        data='test_data/simple/overlay.json').get_json()
    assert isinstance(result, dict)
    assert result['thor'] == 'mythological'

def test_jref_nested():
    result = client().post('/jsonreference',
        data='test_data/simple/overlay.json#/b/2').get_json()
    assert result == "item3"
