"""
FIFA Player Recommendation System - Startup Script
Run this file to start the application
"""

import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)


def main():
    """Check for trained models, then start the development server"""
    models_dir = os.environ.get('MODELS_DIR', os.path.join(PROJECT_ROOT, 'models'))

    # Check if models exist
    if not os.path.exists(os.path.join(models_dir, 'male_model.pkl')) or \
            not os.path.exists(os.path.join(models_dir, 'female_model.pkl')):
        print("=" * 60)
        print("Models not found!")
        print("=" * 60)
        print("\nPlease train the models first by running:")
        print("  python training/train.py")
        print("\nFor training options and help:")
        print("  See training/README.md")
        print("\n" + "=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("FIFA Player Recommendation System")
    print("=" * 60)
    print("\nLoading models...")

    # Importing the app loads the models
    from app.main import app

    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))

    print("\nApplication ready!")
    print(f"\nOpen your browser and go to: http://localhost:{port}")
    print("\n" + "=" * 60)

    # Run the app
    app.run(debug=False, host=host, port=port)


if __name__ == '__main__':
    main()
