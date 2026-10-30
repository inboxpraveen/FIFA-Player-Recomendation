import joblib
import numpy as np

from src.data_processing import DataProcessor
from src.model import PlayerRecommender


def test_features_are_standardized(processed):
    features = processed['normalized_features']
    assert features.shape[1] == len(DataProcessor.FEATURE_COLUMNS) == 35
    assert np.allclose(features.mean(axis=0), 0, atol=1e-6)


def test_recommend_similar_is_ranked_and_excludes_source(model):
    top = model.data.nlargest(1, 'OVR')['Name'].iloc[0]
    results = model.recommend_similar(top, n_recommendations=10)

    assert len(results) == 10
    assert top not in [r['Name'] for r in results]
    scores = [r['similarity_score'] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(-1.0 <= s <= 1.0 for s in scores)


def test_recommend_similar_matches_brute_force(model):
    idx = 0
    X = model.normalized_features.astype(np.float64)
    expected = X @ X[idx] / (np.linalg.norm(X, axis=1) * np.linalg.norm(X[idx]))
    expected[idx] = -np.inf
    best = int(np.argmax(expected))

    name = model.data.iloc[idx]['Name']
    result = model.recommend_similar(name, n_recommendations=1, same_position=False)[0]
    assert result['Name'] == model.data.iloc[best]['Name']
    assert abs(result['similarity_score'] - expected[best]) < 1e-4


def test_filters_are_applied(model):
    name = model.data.iloc[0]['Name']
    source = model.data.iloc[0]

    same_pos = model.recommend_similar(name, n_recommendations=20, same_position=True)
    assert {r['Position_Category'] for r in same_pos} == {source['Position_Category']}

    near_age = model.recommend_similar(name, n_recommendations=20, same_position=False, max_age_diff=1)
    assert all(abs(r['Age'] - source['Age']) <= 1 for r in near_age)


def test_unknown_player_returns_nothing(model):
    assert model.recommend_similar('No Such Player Anywhere') == []
    assert model.get_player_details('No Such Player Anywhere') is None
    assert model.get_player_details('   ') is None


def test_name_lookup_is_case_insensitive_and_partial(model):
    name = model.data.iloc[0]['Name']
    assert model.get_player_details(name.upper())['Name'] == name
    assert model.get_player_details(name[1:-1]) is not None


def test_search_treats_query_as_text(model):
    # Regex characters in user input must not raise or match everything
    assert model.search_players(query='(') == []
    results = model.search_players(min_overall=85, limit=5)
    assert 0 < len(results) <= 5
    assert all(r['OVR'] >= 85 for r in results)


def test_recommend_by_attributes_prefers_matching_profile(model):
    keeper = model.data[model.data['Position_Category'] == 'Goalkeeper'].iloc[0]
    target = {f: float(keeper[f]) for f in model.feature_names}
    results = model.recommend_by_attributes(target, n_recommendations=1)
    assert results[0]['Name'] == keeper['Name']


def test_save_and_load_round_trip(model, tmp_path):
    path = tmp_path / 'model.pkl'
    model.save(str(path))
    loaded = PlayerRecommender.load(str(path))

    name = model.data.iloc[0]['Name']
    original = [r['Name'] for r in model.recommend_similar(name, 5)]
    assert [r['Name'] for r in loaded.recommend_similar(name, 5)] == original


def test_loads_version_2_0_model_files(model, tmp_path):
    """2.0 files carry a full similarity matrix and no scaling statistics"""
    path = tmp_path / 'old_model.pkl'
    joblib.dump({
        'data': model.data,
        'normalized_features': np.zeros_like(model.normalized_features),
        'feature_names': model.feature_names,
        'similarity_matrix': np.zeros((2, 2)),
    }, path)

    loaded = PlayerRecommender.load(str(path))
    name = model.data.iloc[0]['Name']
    original = [r['Name'] for r in model.recommend_similar(name, 5)]
    assert [r['Name'] for r in loaded.recommend_similar(name, 5)] == original
