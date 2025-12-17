# Installation Guide

This guide will help you set up the FIFA Player Recommendation System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (comes with Python)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/inboxpraveen/FIFA-Player-Recomendation.git
cd FIFA-Player-Recomendation
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0 (web framework)
- pandas 2.1.4 (data processing)
- numpy 1.26.2 (numerical operations)
- scikit-learn 1.3.2 (machine learning)
- scipy 1.11.4 (scientific computing)
- joblib 1.3.2 (model persistence)
- gunicorn 21.2.0 (production server)

### 4. Verify Dataset

Ensure the datasets are in place:
```
new-data/
├── male_players.csv    (~16,000 players)
└── female_players.csv  (~1,500 players)
```

### 5. Train the Models

```bash
# Train both models (default)
python training/train.py

# Train only male players model
python training/train.py --male

# Train only female players model
python training/train.py --female

# Skip specific model
python training/train.py --skip-male     # Train female only
python training/train.py --skip-female   # Train male only
```

📖 **For detailed training options and troubleshooting, see [training/README.md](training/README.md)**

This will:
- Load and clean the datasets
- Extract and normalize features
- Train male and female models
- Compute similarity matrices
- Save models to `models/` directory

**Training Time:**
- Male model: ~30 seconds
- Female model: ~2 seconds

**Expected Output:**
```
models/
├── male_model.pkl    (~1 GB)
└── female_model.pkl  (~10 MB)
```

### 6. Run the Application

```bash
python run.py
```

Or directly run the Flask app:
```bash
cd app
python main.py
```

### 7. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the FIFA Player Recommendation System home page!

## Troubleshooting

### Issue: "Models not found"

**Solution:** Train the models first (Step 5)

### Issue: "Module not found" error

**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
pip install -r requirements.txt
```

### Issue: Port 5000 already in use

**Solution:** Use a different port
```bash
# Edit app/main.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use 5001 instead
```

### Issue: Training script not found

**Solution:** Ensure you're in the project root directory
```bash
cd FIFA-Player-Recomendation
python training/train.py
```

### Issue: Large model files not loading

**Solution:** Ensure you have at least 2 GB free RAM

### Issue: CSV parsing errors

**Solution:** Ensure CSV files are UTF-8 encoded

## Verification Checklist

After installation, verify everything works:

- [ ] Application starts without errors
- [ ] Home page loads with statistics
- [ ] Search functionality works
- [ ] Recommendations are generated
- [ ] Player comparison displays radar charts
- [ ] Gender toggle switches between male/female players
- [ ] No console errors in browser DevTools

## Production Deployment

For production deployment, see [Deployment Guide](PROJECT_SUMMARY.md#deployment-guide) in PROJECT_SUMMARY.md.

### Quick Production Setup

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

## System Requirements

### Minimum

- **CPU:** 2 cores
- **RAM:** 2 GB
- **Storage:** 2 GB free space
- **OS:** Windows 10, macOS 10.14+, Ubuntu 18.04+

### Recommended

- **CPU:** 4 cores
- **RAM:** 4 GB
- **Storage:** 5 GB free space
- **OS:** Windows 11, macOS 12+, Ubuntu 20.04+

## Performance Tips

1. **Use SSD** - Faster model loading
2. **Increase RAM** - Better concurrent user support
3. **Use production server** - gunicorn instead of Flask dev server
4. **Enable caching** - Redis for frequently accessed data
5. **Use CDN** - For static assets in production

## Next Steps

Once installed:

1. Read the [README.md](README.md) for usage instructions
2. Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for technical details
3. See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
4. Report issues on [GitHub Issues](https://github.com/inboxpraveen/FIFA-Player-Recomendation/issues)

## Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Search [existing GitHub issues](https://github.com/inboxpraveen/FIFA-Player-Recomendation/issues)
3. Open a new issue with:
   - Your OS and Python version
   - Error messages
   - Steps to reproduce

## Uninstallation

To remove the application:

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf FIFA-Player-Recomendation  # macOS/Linux
# or
rmdir /s /q FIFA-Player-Recomendation  # Windows
```

---

**Happy Recommending! ⚽**

