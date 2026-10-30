def top_name(model):
    return model.data.nlargest(1, 'OVR')['Name'].iloc[0]


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'FIFA' in response.data


def test_health(client, monkeypatch):
    assert client.get('/api/health').get_json() == {'status': 'ok', 'models': {'male': True, 'female': True}}

    from app import main
    monkeypatch.setattr(main, 'male_model', None)
    assert client.get('/api/health').status_code == 503


def test_stats(client):
    body = client.get('/api/stats').get_json()
    assert body['success'] is True
    assert body['female']['total_players'] > 1000


def test_search(client):
    body = client.post('/api/search', json={'gender': 'female', 'min_overall': 85, 'limit': 5}).get_json()
    assert body['success'] is True
    assert 0 < body['count'] <= 5
    assert all(p['overall'] >= 85 for p in body['players'])


def test_search_caps_limit_and_ignores_bad_numbers(client):
    body = client.post('/api/search', json={'gender': 'female', 'limit': 100000, 'min_overall': 'abc'}).get_json()
    assert body['count'] == 100


def test_recommend(client, model):
    name = top_name(model)
    body = client.post('/api/recommend', json={'gender': 'female', 'player_name': name, 'n_recommendations': 5}).get_json()
    assert body['success'] is True
    assert body['source_player']['name'] == name
    assert len(body['recommendations']) == 5
    assert all(0 < r['similarity'] <= 100 for r in body['recommendations'])


def test_recommend_validation(client):
    assert client.post('/api/recommend', json={'gender': 'female'}).status_code == 400
    assert client.post('/api/recommend', data='not json', content_type='text/plain').status_code == 400
    missing = client.post('/api/recommend', json={'gender': 'female', 'player_name': 'No Such Player Anywhere'})
    assert missing.status_code == 404


def test_player_details(client, model):
    name = top_name(model)
    body = client.get(f'/api/player/{name}?gender=female').get_json()
    assert body['player']['name'] == name
    assert len(body['radar']['attributes']) == 6
    assert client.get('/api/player/No%20Such%20Player?gender=female').status_code == 404


def test_compare(client, model):
    names = list(model.data.nlargest(3, 'OVR')['Name'])
    body = client.post('/api/compare', json={'gender': 'female', 'players': names}).get_json()
    assert [p['card']['name'] for p in body['players']] == names
    assert client.post('/api/compare', json={'gender': 'female', 'players': names[:1]}).status_code == 400


def test_top_players(client):
    body = client.get('/api/top-players?gender=female&n=3').get_json()
    overalls = [p['overall'] for p in body['players']]
    assert len(overalls) == 3
    assert overalls == sorted(overalls, reverse=True)


def test_autocomplete(client, model):
    name = top_name(model)
    body = client.get(f'/api/autocomplete?gender=female&query={name[:4]}&limit=500').get_json()
    assert name in body['suggestions']
    assert len(body['suggestions']) <= 20
    assert client.get('/api/autocomplete?gender=female&query=a').get_json()['suggestions'] == []


def test_errors_do_not_leak_details(client, monkeypatch):
    from app import main

    def boom(*args, **kwargs):
        raise RuntimeError('secret internal detail')

    monkeypatch.setattr(main.female_model, 'search_players', boom)
    response = client.post('/api/search', json={'gender': 'female'})
    assert response.status_code == 500
    assert b'secret' not in response.data
