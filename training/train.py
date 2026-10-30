"""
FIFA Player Recommendation System - Model Training Script

Usage:
    python training/train.py                    # Train both models
    python training/train.py --male             # Train male model only
    python training/train.py --female           # Train female model only
    python training/train.py --skip-male        # Train female only
    python training/train.py --skip-female      # Train male only
"""

import sys
import os
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.data_processing import DataProcessor
from src.model import PlayerRecommender


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num, text):
    """Print a step with formatting"""
    print(f"\n[{step_num}] {text}")


def train_model(data_path, model_name, model_path):
    """
    Train a single model
    
    Args:
        data_path: Path to CSV data file
        model_name: Name for display (e.g., "Male Players")
        model_path: Path to save the model
    
    Returns:
        tuple: (success, model, processing_time)
    """
    start_time = time.time()
    
    try:
        print_step(1, f"Processing {model_name} data...")
        
        # Check if data file exists
        if not os.path.exists(data_path):
            print(f"Error: Data file not found: {data_path}")
            return False, None, 0
        
        # Initialize processor
        processor = DataProcessor()
        
        # Process data
        processed = processor.process_for_training(data_path)
        
        print(f"   - Loaded {len(processed['data'])} players")
        print(f"   - Extracted {len(processed['feature_names'])} features")
        print(f"   - Feature matrix shape: {processed['normalized_features'].shape}")
        
        # Train model
        print_step(2, f"Training {model_name} model...")
        
        model = PlayerRecommender()
        model.fit(
            data=processed['data'],
            normalized_features=processed['normalized_features'],
            feature_names=processed['feature_names'],
            feature_mean=processed['feature_mean'],
            feature_std=processed['feature_std']
        )
        
        print(f"   - Indexed {len(model.data)} players for on-demand cosine similarity")
        
        # Save model
        print_step(3, f"Saving {model_name} model...")
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model.save(model_path)
        
        # Get file size
        file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
        
        print(f"   - Model saved: {model_path}")
        print(f"   - File size: {file_size:.1f} MB")
        
        # Test model
        print_step(4, f"Testing {model_name} model...")
        
        # Get top player
        top_player = model.data.nlargest(1, 'OVR')['Name'].values[0]
        print(f"   - Top player: {top_player}")
        
        # Test search
        search_results = model.search_players(limit=5)
        print(f"   - Search test: Found {len(search_results)} players")
        
        # Test recommendations with top player
        try:
            recommendations = model.recommend_similar(top_player, n_recommendations=3)
            print(f"   - Recommendation test: {len(recommendations)} similar players found")
        except Exception as e:
            print(f"   ! Recommendation test skipped: {e}")
        
        processing_time = time.time() - start_time
        
        print(f"\n{model_name} model trained successfully in {processing_time:.1f}s")
        
        return True, model, processing_time
        
    except Exception as e:
        print(f"\nError training {model_name} model:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, 0


def display_summary(results):
    """Display training summary for the models that were requested"""
    print_header("Training Summary")

    print("\nModels trained:")
    for name, success, elapsed in results:
        status = f"{elapsed:.1f}s" if success else "Failed"
        print(f"  {name:<22} - {status}")

    total_time = sum(elapsed for _, success, elapsed in results if success)
    
    print(f"\nTotal training time: {total_time:.1f}s")
    
    if any(success for _, success, _ in results):
        print("\nYou can now run the application:")
        print("   python run.py")
    
    print("\n" + "=" * 70 + "\n")


def main():
    """Main training function"""
    
    # Never crash on a console or log file that cannot encode a player's name
    sys.stdout.reconfigure(errors='replace')

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Train FIFA Player Recommendation Models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python training/train.py                  Train both models
  python training/train.py --male           Train male model only
  python training/train.py --female         Train female model only
  python training/train.py --skip-male      Train female model only
  python training/train.py --skip-female    Train male model only
        '''
    )
    
    parser.add_argument('--male', action='store_true', 
                        help='Train male model only')
    parser.add_argument('--female', action='store_true', 
                        help='Train female model only')
    parser.add_argument('--skip-male', action='store_true', 
                        help='Skip male model training')
    parser.add_argument('--skip-female', action='store_true', 
                        help='Skip female model training')
    
    args = parser.parse_args()
    
    # Determine which models to train
    train_male = True
    train_female = True
    
    # If specific models are requested
    if args.male or args.female:
        train_male = args.male
        train_female = args.female
    
    # Apply skip flags
    if args.skip_male:
        train_male = False
    if args.skip_female:
        train_female = False
    
    # Check if at least one model will be trained
    if not train_male and not train_female:
        print("Error: No models selected for training!")
        print("   Use --male or --female to train specific models")
        sys.exit(1)
    
    # Display header
    print_header("FIFA Player Recommendation System - Model Training")
    
    print("\nModels to train:")
    if train_male:
        print("  - Male Players Model")
    if train_female:
        print("  - Female Players Model")
    
    # Define paths (relative to project root)
    male_data_path = os.path.join(project_root, 'new-data', 'male_players.csv')
    female_data_path = os.path.join(project_root, 'new-data', 'female_players.csv')
    male_model_path = os.path.join(project_root, 'models', 'male_model.pkl')
    female_model_path = os.path.join(project_root, 'models', 'female_model.pkl')
    
    # Train models
    male_success = False
    male_time = 0
    female_success = False
    female_time = 0
    
    if train_male:
        print_header("Training Male Players Model")
        male_success, male_model, male_time = train_model(
            male_data_path, 
            "Male Players", 
            male_model_path
        )
    
    if train_female:
        print_header("Training Female Players Model")
        female_success, female_model, female_time = train_model(
            female_data_path, 
            "Female Players", 
            female_model_path
        )
    
    # Display summary
    results = []
    if train_male:
        results.append(("Male Players Model", male_success, male_time))
    if train_female:
        results.append(("Female Players Model", female_success, female_time))
    display_summary(results)
    
    # Exit with appropriate code
    if (train_male and not male_success) or (train_female and not female_success):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

