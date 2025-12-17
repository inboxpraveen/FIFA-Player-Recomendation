"""
Data Processing Module
Handles data loading, cleaning, and preprocessing for FIFA player datasets
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import re


class DataProcessor:
    """Process FIFA player data for model training and inference"""
    
    # Core attributes for player comparison
    FEATURE_COLUMNS = [
        'PAC', 'SHO', 'PAS', 'DRI', 'DEF', 'PHY',
        'Acceleration', 'Sprint Speed', 'Positioning', 'Finishing',
        'Shot Power', 'Long Shots', 'Volleys', 'Penalties',
        'Vision', 'Crossing', 'Free Kick Accuracy', 'Short Passing',
        'Long Passing', 'Curve', 'Dribbling', 'Agility', 'Balance',
        'Reactions', 'Ball Control', 'Composure', 'Interceptions',
        'Heading Accuracy', 'Def Awareness', 'Standing Tackle',
        'Sliding Tackle', 'Jumping', 'Stamina', 'Strength', 'Aggression'
    ]
    
    # Columns to keep for display
    DISPLAY_COLUMNS = [
        'Name', 'OVR', 'Position', 'Age', 'Nation', 'League', 'Team',
        'Height', 'Weight', 'Preferred foot', 'Weak foot', 'Skill moves'
    ]
    
    def __init__(self):
        self.male_data = None
        self.female_data = None
        
    def load_data(self, male_path: str, female_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load male and female player datasets"""
        print("Loading datasets...")
        
        # Load datasets
        self.male_data = pd.read_csv(male_path)
        self.female_data = pd.read_csv(female_path)
        
        # Drop unnecessary index columns
        if 'Unnamed: 0' in self.male_data.columns:
            self.male_data = self.male_data.drop('Unnamed: 0', axis=1)
        if 'Unnamed: 0' in self.female_data.columns:
            self.female_data = self.female_data.drop('Unnamed: 0', axis=1)
            
        print(f"Loaded {len(self.male_data)} male players and {len(self.female_data)} female players")
        
        return self.male_data, self.female_data
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess player data"""
        df = df.copy()
        
        # Remove players with missing critical attributes
        critical_cols = ['Name', 'OVR', 'Position'] + self.FEATURE_COLUMNS
        df = df.dropna(subset=critical_cols)
        
        # Fill missing display columns with defaults
        df['Age'] = df['Age'].fillna(0).astype(int)
        df['Nation'] = df['Nation'].fillna('Unknown')
        df['League'] = df['League'].fillna('Unknown')
        df['Team'] = df['Team'].fillna('Free Agent')
        df['Preferred foot'] = df['Preferred foot'].fillna('Right')
        df['Weak foot'] = df['Weak foot'].fillna(3).astype(int)
        df['Skill moves'] = df['Skill moves'].fillna(2).astype(int)
        df['Height'] = df['Height'].fillna('N/A')
        df['Weight'] = df['Weight'].fillna('N/A')
        
        # Ensure all feature columns are numeric
        for col in self.FEATURE_COLUMNS:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Remove duplicates based on player name
        df = df.drop_duplicates(subset=['Name'], keep='first')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        print(f"Cleaned data: {len(df)} players remaining")
        
        return df
    
    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract feature matrix for similarity calculations"""
        features = df[self.FEATURE_COLUMNS].values
        return features
    
    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to 0-1 range for fair comparison"""
        # Use min-max normalization
        min_vals = features.min(axis=0)
        max_vals = features.max(axis=0)
        
        # Avoid division by zero
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        normalized = (features - min_vals) / range_vals
        
        return normalized
    
    def get_position_category(self, position: str) -> str:
        """Categorize position into broader groups"""
        position = str(position).upper()
        
        if position in ['GK']:
            return 'Goalkeeper'
        elif any(pos in position for pos in ['CB', 'LB', 'RB', 'LWB', 'RWB']):
            return 'Defender'
        elif any(pos in position for pos in ['CDM', 'CM', 'CAM', 'LM', 'RM']):
            return 'Midfielder'
        elif any(pos in position for pos in ['ST', 'CF', 'LW', 'RW', 'LF', 'RF']):
            return 'Forward'
        else:
            return 'Unknown'
    
    def process_for_training(self, data_path: str) -> Dict:
        """Process data and return everything needed for training"""
        df = pd.read_csv(data_path)
        
        # Drop unnecessary index column
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)
        
        # Clean data
        df = self.clean_data(df)
        
        # Add position category
        df['Position_Category'] = df['Position'].apply(self.get_position_category)
        
        # Extract and normalize features
        features = self.extract_features(df)
        normalized_features = self.normalize_features(features)
        
        return {
            'data': df,
            'features': features,
            'normalized_features': normalized_features,
            'feature_names': self.FEATURE_COLUMNS
        }
    
    def get_player_card_data(self, player_row: pd.Series) -> Dict:
        """Extract player data formatted for display cards"""
        return {
            'name': player_row.get('Name', 'Unknown'),
            'overall': int(player_row.get('OVR', 0)),
            'position': player_row.get('Position', 'N/A'),
            'age': int(player_row.get('Age', 0)),
            'nation': player_row.get('Nation', 'Unknown'),
            'league': player_row.get('League', 'Unknown'),
            'team': player_row.get('Team', 'Free Agent'),
            'height': player_row.get('Height', 'N/A'),
            'weight': player_row.get('Weight', 'N/A'),
            'preferred_foot': player_row.get('Preferred foot', 'Right'),
            'weak_foot': int(player_row.get('Weak foot', 3)),
            'skill_moves': int(player_row.get('Skill moves', 2)),
            'pace': int(player_row.get('PAC', 0)),
            'shooting': int(player_row.get('SHO', 0)),
            'passing': int(player_row.get('PAS', 0)),
            'dribbling': int(player_row.get('DRI', 0)),
            'defending': int(player_row.get('DEF', 0)),
            'physical': int(player_row.get('PHY', 0)),
        }
    
    def get_radar_chart_data(self, player_row: pd.Series) -> Dict:
        """Extract attributes for radar chart comparison"""
        return {
            'name': player_row.get('Name', 'Unknown'),
            'attributes': {
                'Pace': int(player_row.get('PAC', 0)),
                'Shooting': int(player_row.get('SHO', 0)),
                'Passing': int(player_row.get('PAS', 0)),
                'Dribbling': int(player_row.get('DRI', 0)),
                'Defending': int(player_row.get('DEF', 0)),
                'Physical': int(player_row.get('PHY', 0))
            },
            'detailed_attributes': {
                'Acceleration': int(player_row.get('Acceleration', 0)),
                'Sprint Speed': int(player_row.get('Sprint Speed', 0)),
                'Positioning': int(player_row.get('Positioning', 0)),
                'Finishing': int(player_row.get('Finishing', 0)),
                'Shot Power': int(player_row.get('Shot Power', 0)),
                'Long Shots': int(player_row.get('Long Shots', 0)),
                'Vision': int(player_row.get('Vision', 0)),
                'Crossing': int(player_row.get('Crossing', 0)),
                'Short Passing': int(player_row.get('Short Passing', 0)),
                'Long Passing': int(player_row.get('Long Passing', 0)),
                'Dribbling': int(player_row.get('Dribbling', 0)),
                'Ball Control': int(player_row.get('Ball Control', 0)),
                'Agility': int(player_row.get('Agility', 0)),
                'Balance': int(player_row.get('Balance', 0)),
                'Interceptions': int(player_row.get('Interceptions', 0)),
                'Heading Accuracy': int(player_row.get('Heading Accuracy', 0)),
                'Def Awareness': int(player_row.get('Def Awareness', 0)),
                'Standing Tackle': int(player_row.get('Standing Tackle', 0)),
                'Sliding Tackle': int(player_row.get('Sliding Tackle', 0)),
                'Jumping': int(player_row.get('Jumping', 0)),
                'Stamina': int(player_row.get('Stamina', 0)),
                'Strength': int(player_row.get('Strength', 0)),
                'Aggression': int(player_row.get('Aggression', 0))
            }
        }

