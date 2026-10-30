"""
Recommendation Model Module
Implements fast, efficient content-based player recommendation system
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
import joblib


class PlayerRecommender:
    """
    Fast and accurate player recommendation system using content-based filtering
    with cosine similarity on standardized player attributes.

    Similarity is computed on demand: one query is a single matrix-vector
    product over the feature matrix, so there is no n x n matrix to build,
    store or load.
    """

    def __init__(self):
        self.data = None
        self.features = None
        self.normalized_features = None
        self.feature_names = None
        self.feature_mean = None
        self.feature_std = None
        self._norms = None
        self._names_lower = None

    def fit(
        self,
        data: pd.DataFrame,
        normalized_features: np.ndarray,
        feature_names: List[str],
        feature_mean: np.ndarray = None,
        feature_std: np.ndarray = None
    ):
        """
        Fit the recommender with player data and features

        Args:
            data: DataFrame with player information
            normalized_features: Standardized feature matrix
            feature_names: List of feature column names
            feature_mean: Per-feature mean used for standardization
            feature_std: Per-feature std used for standardization
        """
        self.data = data.reset_index(drop=True)
        self.normalized_features = np.asarray(normalized_features, dtype=np.float32)
        self.feature_names = list(feature_names)
        self.feature_mean = feature_mean
        self.feature_std = feature_std
        self._build_index()

    def _build_index(self):
        """Precompute row norms and lowercase names used by every query"""
        self._norms = np.linalg.norm(self.normalized_features, axis=1)
        self._names_lower = self.data['Name'].str.lower()

    def _cosine_scores(self, vector: np.ndarray) -> np.ndarray:
        """Cosine similarity between one vector and every player"""
        denom = self._norms * np.linalg.norm(vector) + 1e-12
        return (self.normalized_features @ vector) / denom

    def _top_n(self, scores: np.ndarray, mask: np.ndarray, n: int) -> List[tuple]:
        """Return (index, score) pairs for the n best scores where mask is True"""
        candidates = np.flatnonzero(mask)
        if len(candidates) == 0 or n <= 0:
            return []

        candidate_scores = scores[candidates]
        k = min(n, len(candidates))
        top = np.argpartition(-candidate_scores, k - 1)[:k]
        top = top[np.argsort(-candidate_scores[top], kind='stable')]

        return [(int(candidates[i]), float(candidate_scores[i])) for i in top]

    def _to_records(self, ranked: List[tuple], score_key: str) -> List[Dict]:
        """Turn (index, score) pairs into player dictionaries"""
        records = []
        for idx, score in ranked:
            player_data = self.data.iloc[idx].to_dict()
            player_data[score_key] = score
            records.append(player_data)
        return records

    def recommend_similar(
        self,
        player_name: str,
        n_recommendations: int = 10,
        same_position: bool = True,
        max_age_diff: int = None
    ) -> List[Dict]:
        """
        Recommend similar players based on attributes

        Args:
            player_name: Name of the player to find similar players for
            n_recommendations: Number of recommendations to return
            same_position: Whether to filter by same position category
            max_age_diff: Maximum age difference for recommendations (None for no limit)

        Returns:
            List of dictionaries containing player information and similarity scores
        """
        # Find player index
        player_idx = self._find_player_index(player_name)
        if player_idx is None:
            return []

        scores = self._cosine_scores(self.normalized_features[player_idx])

        # Build the candidate mask, skipping the player itself
        mask = np.ones(len(self.data), dtype=bool)
        mask[player_idx] = False

        player_info = self.data.iloc[player_idx]
        player_position = player_info.get('Position_Category', None)
        player_age = player_info.get('Age', None)

        # Apply position filter
        if same_position and player_position and 'Position_Category' in self.data:
            mask &= (self.data['Position_Category'] == player_position).to_numpy()

        # Apply age filter
        if max_age_diff is not None and player_age is not None:
            ages = self.data['Age'].to_numpy()
            mask &= np.abs(ages - player_age) <= max_age_diff

        ranked = self._top_n(scores, mask, n_recommendations)
        return self._to_records(ranked, 'similarity_score')

    def recommend_by_attributes(
        self,
        target_attributes: Dict[str, float],
        n_recommendations: int = 10,
        position: str = None
    ) -> List[Dict]:
        """
        Recommend players based on custom attribute preferences

        Args:
            target_attributes: Dictionary of attribute names and values (0-100)
            n_recommendations: Number of recommendations to return
            position: Filter by position category

        Returns:
            List of dictionaries containing player information and match scores
        """
        # Create target feature vector, defaulting missing attributes to the average player
        target_vector = np.array([
            target_attributes.get(feature, self.feature_mean[i])
            for i, feature in enumerate(self.feature_names)
        ], dtype=np.float64)

        # Scale with the same statistics used at training time
        target_vector = (target_vector - self.feature_mean) / self.feature_std

        scores = self._cosine_scores(target_vector.astype(np.float32))

        mask = np.ones(len(self.data), dtype=bool)
        if position:
            mask &= (self.data['Position_Category'] == position).to_numpy()

        ranked = self._top_n(scores, mask, n_recommendations)
        return self._to_records(ranked, 'match_score')

    def search_players(
        self,
        query: str = None,
        position: str = None,
        min_overall: int = None,
        max_overall: int = None,
        nation: str = None,
        league: str = None,
        team: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search players with various filters

        Args:
            query: Search query for player name
            position: Filter by position
            min_overall: Minimum overall rating
            max_overall: Maximum overall rating
            nation: Filter by nation
            league: Filter by league
            team: Filter by team
            limit: Maximum number of results

        Returns:
            List of player dictionaries
        """
        df = self.data

        # Apply filters
        if query:
            df = df[self._names_lower[df.index].str.contains(query.lower(), regex=False, na=False)]

        if position:
            df = df[df['Position'].str.contains(position, case=False, regex=False, na=False)]

        if min_overall is not None:
            df = df[df['OVR'] >= min_overall]

        if max_overall is not None:
            df = df[df['OVR'] <= max_overall]

        if nation:
            df = df[df['Nation'].str.contains(nation, case=False, regex=False, na=False)]

        if league:
            df = df[df['League'].str.contains(league, case=False, regex=False, na=False)]

        if team:
            df = df[df['Team'].str.contains(team, case=False, regex=False, na=False)]

        # Sort by overall rating
        df = df.sort_values('OVR', ascending=False)

        # Limit results
        df = df.head(limit)

        return df.to_dict('records')

    def get_player_details(self, player_name: str) -> Optional[Dict]:
        """Get detailed information for a specific player"""
        player_idx = self._find_player_index(player_name)
        if player_idx is None:
            return None

        return self.data.iloc[player_idx].to_dict()

    def get_top_players(self, n: int = 100, position: str = None) -> List[Dict]:
        """
        Get top N players by overall rating

        Args:
            n: Number of players to return
            position: Filter by position category

        Returns:
            List of player dictionaries
        """
        df = self.data

        if position:
            df = df[df['Position_Category'] == position]

        df = df.sort_values('OVR', ascending=False).head(n)

        return df.to_dict('records')

    def _find_player_index(self, player_name: str) -> Optional[int]:
        """Find the index of a player by name (case-insensitive)"""
        player_name_lower = player_name.strip().lower()
        if not player_name_lower:
            return None

        matches = self._names_lower.index[self._names_lower == player_name_lower]

        if len(matches) == 0:
            # Fall back to a partial match, preferring the highest rated player
            partial = self._names_lower.str.contains(player_name_lower, regex=False, na=False)
            if not partial.any():
                return None
            return int(self.data.loc[partial, 'OVR'].idxmax())

        return int(matches[0])

    def save(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'data': self.data,
            'normalized_features': self.normalized_features,
            'feature_names': self.feature_names,
            'feature_mean': self.feature_mean,
            'feature_std': self.feature_std
        }
        joblib.dump(model_data, filepath, compress=3)
        print(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: str):
        """
        Load a trained model.

        Models saved by version 2.0 also carry a full similarity matrix and
        min-max scaled features. The matrix is ignored and the features are
        re-standardized from the stored player data, so old files keep working.
        """
        model_data = joblib.load(filepath)

        model = cls()
        model.data = model_data['data'].reset_index(drop=True)
        model.feature_names = list(model_data['feature_names'])
        model.feature_mean = model_data.get('feature_mean')
        model.feature_std = model_data.get('feature_std')

        if model.feature_mean is None or model.feature_std is None:
            raw = model.data[model.feature_names].to_numpy(dtype=np.float64)
            model.feature_mean = raw.mean(axis=0)
            model.feature_std = raw.std(axis=0)
            model.feature_std[model.feature_std == 0] = 1
            model.normalized_features = ((raw - model.feature_mean) / model.feature_std).astype(np.float32)
            print(f"Upgraded a 2.0 model file in memory; retrain to shrink {filepath}")
        else:
            model.normalized_features = np.asarray(model_data['normalized_features'], dtype=np.float32)

        model._build_index()

        print(f"Model loaded from {filepath}")
        return model
