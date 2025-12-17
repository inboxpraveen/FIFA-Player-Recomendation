"""
Recommendation Model Module
Implements fast, efficient content-based player recommendation system
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import joblib


class PlayerRecommender:
    """
    Fast and accurate player recommendation system using content-based filtering
    with cosine similarity on normalized player attributes
    """
    
    def __init__(self):
        self.data = None
        self.features = None
        self.normalized_features = None
        self.feature_names = None
        self.similarity_matrix = None
        
    def fit(self, data: pd.DataFrame, normalized_features: np.ndarray, feature_names: List[str]):
        """
        Fit the recommender with player data and features
        
        Args:
            data: DataFrame with player information
            normalized_features: Normalized feature matrix
            feature_names: List of feature column names
        """
        self.data = data
        self.normalized_features = normalized_features
        self.feature_names = feature_names
        
        # Precompute similarity matrix for fast recommendations
        print("Computing similarity matrix...")
        self.similarity_matrix = cosine_similarity(normalized_features)
        print(f"Similarity matrix computed: {self.similarity_matrix.shape}")
        
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
        
        # Get similarity scores
        similarity_scores = self.similarity_matrix[player_idx]
        
        # Get player info
        player_info = self.data.iloc[player_idx]
        player_position = player_info.get('Position_Category', None)
        player_age = player_info.get('Age', None)
        
        # Create candidate list with filters
        candidates = []
        for idx, score in enumerate(similarity_scores):
            if idx == player_idx:  # Skip the player itself
                continue
                
            candidate = self.data.iloc[idx]
            
            # Apply position filter
            if same_position and player_position:
                if candidate.get('Position_Category') != player_position:
                    continue
            
            # Apply age filter
            if max_age_diff is not None and player_age is not None:
                candidate_age = candidate.get('Age', None)
                if candidate_age is not None:
                    if abs(candidate_age - player_age) > max_age_diff:
                        continue
            
            candidates.append((idx, score))
        
        # Sort by similarity score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations
        recommendations = []
        for idx, score in candidates[:n_recommendations]:
            player_data = self.data.iloc[idx].to_dict()
            player_data['similarity_score'] = float(score)
            recommendations.append(player_data)
        
        return recommendations
    
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
        # Create target feature vector
        target_vector = np.zeros(len(self.feature_names))
        for i, feature in enumerate(self.feature_names):
            target_vector[i] = target_attributes.get(feature, 50)  # Default to 50
        
        # Normalize target vector
        target_vector = (target_vector - target_vector.min()) / (target_vector.max() - target_vector.min() + 1e-8)
        target_vector = target_vector.reshape(1, -1)
        
        # Calculate similarity with all players
        similarities = cosine_similarity(target_vector, self.normalized_features)[0]
        
        # Create candidate list
        candidates = []
        for idx, score in enumerate(similarities):
            candidate = self.data.iloc[idx]
            
            # Apply position filter
            if position:
                if candidate.get('Position_Category') != position:
                    continue
            
            candidates.append((idx, score))
        
        # Sort by similarity score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Get top N recommendations
        recommendations = []
        for idx, score in candidates[:n_recommendations]:
            player_data = self.data.iloc[idx].to_dict()
            player_data['match_score'] = float(score)
            recommendations.append(player_data)
        
        return recommendations
    
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
        df = self.data.copy()
        
        # Apply filters
        if query:
            query_lower = query.lower()
            df = df[df['Name'].str.lower().str.contains(query_lower, na=False)]
        
        if position:
            df = df[df['Position'].str.contains(position, case=False, na=False)]
        
        if min_overall is not None:
            df = df[df['OVR'] >= min_overall]
        
        if max_overall is not None:
            df = df[df['OVR'] <= max_overall]
        
        if nation:
            df = df[df['Nation'].str.contains(nation, case=False, na=False)]
        
        if league:
            df = df[df['League'].str.contains(league, case=False, na=False)]
        
        if team:
            df = df[df['Team'].str.contains(team, case=False, na=False)]
        
        # Sort by overall rating
        df = df.sort_values('OVR', ascending=False)
        
        # Limit results
        df = df.head(limit)
        
        return df.to_dict('records')
    
    def get_player_details(self, player_name: str) -> Dict:
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
        df = self.data.copy()
        
        if position:
            df = df[df['Position_Category'] == position]
        
        df = df.sort_values('OVR', ascending=False).head(n)
        
        return df.to_dict('records')
    
    def _find_player_index(self, player_name: str) -> int:
        """Find the index of a player by name (case-insensitive)"""
        player_name_lower = player_name.lower()
        matches = self.data[self.data['Name'].str.lower() == player_name_lower]
        
        if len(matches) == 0:
            # Try partial match
            matches = self.data[self.data['Name'].str.lower().str.contains(player_name_lower, na=False)]
        
        if len(matches) == 0:
            return None
        
        return matches.index[0]
    
    def save(self, filepath: str):
        """Save the trained model"""
        model_data = {
            'data': self.data,
            'normalized_features': self.normalized_features,
            'feature_names': self.feature_names,
            'similarity_matrix': self.similarity_matrix
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load a trained model"""
        model_data = joblib.load(filepath)
        
        model = cls()
        model.data = model_data['data']
        model.normalized_features = model_data['normalized_features']
        model.feature_names = model_data['feature_names']
        model.similarity_matrix = model_data['similarity_matrix']
        
        print(f"Model loaded from {filepath}")
        return model

