"""
Utility Functions
Helper functions for the FIFA Player Recommendation System
"""

import os
import json
from typing import Dict, List


def ensure_dir(directory: str):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)


def format_player_name(name: str) -> str:
    """Format player name for display"""
    return name.strip().title()


def calculate_match_percentage(similarity_score: float) -> int:
    """Convert similarity score to match percentage"""
    return int(similarity_score * 100)


def get_position_color(position: str) -> str:
    """Get color code for position category"""
    position = position.upper()
    
    if 'GK' in position:
        return '#FFD700'  # Gold
    elif any(p in position for p in ['CB', 'LB', 'RB', 'LWB', 'RWB']):
        return '#4169E1'  # Royal Blue
    elif any(p in position for p in ['CDM', 'CM', 'CAM', 'LM', 'RM']):
        return '#32CD32'  # Lime Green
    elif any(p in position for p in ['ST', 'CF', 'LW', 'RW', 'LF', 'RF']):
        return '#FF4500'  # Orange Red
    else:
        return '#808080'  # Gray


def get_overall_color(overall: int) -> str:
    """Get color code based on overall rating"""
    if overall >= 90:
        return '#FFD700'  # Gold
    elif overall >= 85:
        return '#FF4500'  # Orange
    elif overall >= 80:
        return '#32CD32'  # Green
    elif overall >= 75:
        return '#4169E1'  # Blue
    else:
        return '#808080'  # Gray


def format_player_stats(player_data: Dict) -> Dict:
    """Format player statistics for display"""
    return {
        'name': player_data.get('Name', 'Unknown'),
        'overall': int(player_data.get('OVR', 0)),
        'position': player_data.get('Position', 'N/A'),
        'age': int(player_data.get('Age', 0)),
        'nation': player_data.get('Nation', 'Unknown'),
        'league': player_data.get('League', 'Unknown'),
        'team': player_data.get('Team', 'Free Agent'),
        'attributes': {
            'pace': int(player_data.get('PAC', 0)),
            'shooting': int(player_data.get('SHO', 0)),
            'passing': int(player_data.get('PAS', 0)),
            'dribbling': int(player_data.get('DRI', 0)),
            'defending': int(player_data.get('DEF', 0)),
            'physical': int(player_data.get('PHY', 0))
        }
    }


def validate_player_name(name: str) -> bool:
    """Validate player name input"""
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    if len(name) < 2 or len(name) > 100:
        return False
    
    return True


def get_stat_description(stat_value: int) -> str:
    """Get description for stat value"""
    if stat_value >= 90:
        return "Exceptional"
    elif stat_value >= 80:
        return "Excellent"
    elif stat_value >= 70:
        return "Good"
    elif stat_value >= 60:
        return "Average"
    else:
        return "Below Average"

