"""
Flask Application - FIFA Player Recommendation System
Main application file with API endpoints
"""

from flask import Flask, render_template, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import PlayerRecommender
from src.data_processing import DataProcessor

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global models
male_model = None
female_model = None
data_processor = DataProcessor()


def load_models():
    """Load pre-trained models"""
    global male_model, female_model
    
    try:
        male_model = PlayerRecommender.load('models/male_model.pkl')
        print("Male model loaded successfully")
    except Exception as e:
        print(f"Error loading male model: {e}")
        male_model = None
    
    try:
        female_model = PlayerRecommender.load('models/female_model.pkl')
        print("Female model loaded successfully")
    except Exception as e:
        print(f"Error loading female model: {e}")
        female_model = None


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search_players():
    """Search for players with filters"""
    try:
        data = request.get_json()
        gender = data.get('gender', 'male')
        query = data.get('query', '')
        position = data.get('position')
        min_overall = data.get('min_overall')
        max_overall = data.get('max_overall')
        nation = data.get('nation')
        league = data.get('league')
        team = data.get('team')
        limit = data.get('limit', 50)
        
        # Select model
        model = male_model if gender == 'male' else female_model
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Search players
        results = model.search_players(
            query=query,
            position=position,
            min_overall=min_overall,
            max_overall=max_overall,
            nation=nation,
            league=league,
            team=team,
            limit=limit
        )
        
        # Format results for display
        formatted_results = []
        for player in results:
            formatted_results.append({
                'name': player.get('Name', 'Unknown'),
                'overall': int(player.get('OVR', 0)),
                'position': player.get('Position', 'N/A'),
                'age': int(player.get('Age', 0)),
                'nation': player.get('Nation', 'Unknown'),
                'league': player.get('League', 'Unknown'),
                'team': player.get('Team', 'Free Agent'),
                'pace': int(player.get('PAC', 0)),
                'shooting': int(player.get('SHO', 0)),
                'passing': int(player.get('PAS', 0)),
                'dribbling': int(player.get('DRI', 0)),
                'defending': int(player.get('DEF', 0)),
                'physical': int(player.get('PHY', 0))
            })
        
        return jsonify({
            'success': True,
            'players': formatted_results,
            'count': len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend', methods=['POST'])
def recommend_similar():
    """Get similar player recommendations"""
    try:
        data = request.get_json()
        gender = data.get('gender', 'male')
        player_name = data.get('player_name', '')
        n_recommendations = data.get('n_recommendations', 10)
        same_position = data.get('same_position', True)
        max_age_diff = data.get('max_age_diff')
        
        if not player_name:
            return jsonify({'error': 'Player name is required'}), 400
        
        # Select model
        model = male_model if gender == 'male' else female_model
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get recommendations
        recommendations = model.recommend_similar(
            player_name=player_name,
            n_recommendations=n_recommendations,
            same_position=same_position,
            max_age_diff=max_age_diff
        )
        
        if not recommendations:
            return jsonify({
                'success': False,
                'error': 'Player not found or no recommendations available'
            }), 404
        
        # Get source player details
        source_player = model.get_player_details(player_name)
        
        # Format results
        formatted_recommendations = []
        for player in recommendations:
            formatted_recommendations.append({
                'name': player.get('Name', 'Unknown'),
                'overall': int(player.get('OVR', 0)),
                'position': player.get('Position', 'N/A'),
                'age': int(player.get('Age', 0)),
                'nation': player.get('Nation', 'Unknown'),
                'league': player.get('League', 'Unknown'),
                'team': player.get('Team', 'Free Agent'),
                'similarity': round(player.get('similarity_score', 0) * 100, 1),
                'pace': int(player.get('PAC', 0)),
                'shooting': int(player.get('SHO', 0)),
                'passing': int(player.get('PAS', 0)),
                'dribbling': int(player.get('DRI', 0)),
                'defending': int(player.get('DEF', 0)),
                'physical': int(player.get('PHY', 0))
            })
        
        return jsonify({
            'success': True,
            'source_player': {
                'name': source_player.get('Name', 'Unknown'),
                'overall': int(source_player.get('OVR', 0)),
                'position': source_player.get('Position', 'N/A'),
                'age': int(source_player.get('Age', 0)),
                'nation': source_player.get('Nation', 'Unknown'),
                'league': source_player.get('League', 'Unknown'),
                'team': source_player.get('Team', 'Free Agent')
            },
            'recommendations': formatted_recommendations
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_details(player_name):
    """Get detailed player information"""
    try:
        gender = request.args.get('gender', 'male')
        
        # Select model
        model = male_model if gender == 'male' else female_model
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get player details
        player = model.get_player_details(player_name)
        
        if player is None:
            return jsonify({'error': 'Player not found'}), 404
        
        # Format for display
        player_data = data_processor.get_player_card_data(player)
        radar_data = data_processor.get_radar_chart_data(player)
        
        return jsonify({
            'success': True,
            'player': player_data,
            'radar': radar_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_players():
    """Compare two or more players"""
    try:
        data = request.get_json()
        gender = data.get('gender', 'male')
        player_names = data.get('players', [])
        
        if len(player_names) < 2:
            return jsonify({'error': 'At least 2 players required for comparison'}), 400
        
        if len(player_names) > 4:
            return jsonify({'error': 'Maximum 4 players can be compared'}), 400
        
        # Select model
        model = male_model if gender == 'male' else female_model
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get player data
        players_data = []
        for name in player_names:
            player = model.get_player_details(name)
            if player is None:
                return jsonify({'error': f'Player not found: {name}'}), 404
            
            card_data = data_processor.get_player_card_data(player)
            radar_data = data_processor.get_radar_chart_data(player)
            
            players_data.append({
                'card': card_data,
                'radar': radar_data
            })
        
        return jsonify({
            'success': True,
            'players': players_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/top-players', methods=['GET'])
def get_top_players():
    """Get top players by overall rating"""
    try:
        gender = request.args.get('gender', 'male')
        n = int(request.args.get('n', 100))
        position = request.args.get('position')
        
        # Select model
        model = male_model if gender == 'male' else female_model
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Get top players
        players = model.get_top_players(n=n, position=position)
        
        # Format results
        formatted_players = []
        for player in players:
            formatted_players.append({
                'name': player.get('Name', 'Unknown'),
                'overall': int(player.get('OVR', 0)),
                'position': player.get('Position', 'N/A'),
                'age': int(player.get('Age', 0)),
                'nation': player.get('Nation', 'Unknown'),
                'team': player.get('Team', 'Free Agent')
            })
        
        return jsonify({
            'success': True,
            'players': formatted_players
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dataset statistics"""
    try:
        male_stats = {
            'total_players': len(male_model.data) if male_model else 0,
            'avg_overall': float(male_model.data['OVR'].mean()) if male_model else 0,
            'top_rated': male_model.data.nlargest(1, 'OVR')['Name'].values[0] if male_model else 'N/A'
        }
        
        female_stats = {
            'total_players': len(female_model.data) if female_model else 0,
            'avg_overall': float(female_model.data['OVR'].mean()) if female_model else 0,
            'top_rated': female_model.data.nlargest(1, 'OVR')['Name'].values[0] if female_model else 'N/A'
        }
        
        return jsonify({
            'success': True,
            'male': male_stats,
            'female': female_stats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Load models
    load_models()
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000)

