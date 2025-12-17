"""
FIFA Player Recommendation System - Startup Script
Run this file to start the application
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Check if models exist
if not os.path.exists('models/male_model.pkl') or not os.path.exists('models/female_model.pkl'):
    print("=" * 60)
    print("⚠️  Models not found!")
    print("=" * 60)
    print("\nPlease train the models first by running:")
    print("  python training/train.py")
    print("\nFor training options and help:")
    print("  See training/README.md")
    print("\n" + "=" * 60)
    sys.exit(1)

# Import and run Flask app
from app.main import app, load_models

if __name__ == '__main__':
    print("=" * 60)
    print("🎮 FIFA Player Recommendation System")
    print("=" * 60)
    print("\nLoading models...")
    
    load_models()
    
    print("\n✅ Application ready!")
    print(f"\n🌐 Open your browser and go to: http://localhost:5000")
    print("\n" + "=" * 60)
    
    # Run the app
    app.run(debug=False, host='0.0.0.0', port=5000)

