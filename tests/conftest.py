import os
import sys

import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from src.data_processing import DataProcessor
from src.model import PlayerRecommender

FEMALE_CSV = os.path.join(PROJECT_ROOT, 'new-data', 'female_players.csv')


@pytest.fixture(scope='session')
def processed():
    """The female dataset is small enough to train in well under a second"""
    return DataProcessor().process_for_training(FEMALE_CSV)


@pytest.fixture(scope='session')
def model(processed):
    recommender = PlayerRecommender()
    recommender.fit(
        data=processed['data'],
        normalized_features=processed['normalized_features'],
        feature_names=processed['feature_names'],
        feature_mean=processed['feature_mean'],
        feature_std=processed['feature_std']
    )
    return recommender


@pytest.fixture()
def client(model, monkeypatch):
    from app import main

    monkeypatch.setattr(main, 'male_model', model)
    monkeypatch.setattr(main, 'female_model', model)
    main.app.config['TESTING'] = True
    with main.app.test_client() as test_client:
        yield test_client
