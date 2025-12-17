# Model Training Guide

Complete guide for training the FIFA Player Recommendation System models.

## Quick Start

**Train both models with one command:**

```bash
python training/train.py
```

That's it! Both models will be trained and saved to the `models/` directory.

---

## Table of Contents

1. [Training Options](#training-options)
2. [What Happens During Training](#what-happens-during-training)
3. [Training Output](#training-output)
4. [System Requirements](#system-requirements)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Usage](#advanced-usage)

---

## Training Options

### Train Both Models (Default)

```bash
python training/train.py
```

Trains both male and female player models.

**Output:**
- `models/male_model.pkl` (~1 GB)
- `models/female_model.pkl` (~10 MB)

**Time:** ~30-35 seconds total

### Train Male Model Only

```bash
python training/train.py --male
```

**Use case:** When you only need male player recommendations.

### Train Female Model Only

```bash
python training/train.py --female
```

**Use case:** When you only need female player recommendations.

### Skip Specific Models

```bash
# Train female only (skip male)
python training/train.py --skip-male

# Train male only (skip female)
python training/train.py --skip-female
```

---

## What Happens During Training

### Step 1: Data Loading 📊
- Loads player data from CSV files in `new-data/`
- Validates data file existence and integrity
- Displays player count

### Step 2: Data Processing 🔧
- Cleans data (removes missing values, duplicates)
- Extracts 34 player attributes (PAC, SHO, PAS, DRI, DEF, PHY + sub-attributes)
- Normalizes features to 0-1 scale using min-max normalization
- Creates position categories (Goalkeeper, Defender, Midfielder, Forward)

### Step 3: Model Training 🤖
- Computes similarity matrix using cosine similarity
- Precomputes all player-to-player similarities (n×n matrix)
- This is the most time-intensive step

### Step 4: Model Saving 💾
- Saves model to disk using joblib
- Includes: player data, features, similarity matrix

### Step 5: Model Testing 🧪
- Verifies model works correctly
- Tests search functionality
- Tests recommendation functionality

---

## Training Output

Example output when training both models:

```
======================================================================
  ⚽ FIFA Player Recommendation System - Model Training
======================================================================

Models to train:
  • Male Players Model
  • Female Players Model

======================================================================
  🔵 Training Male Players Model
======================================================================

[📊] Processing Male Players data...
   ✓ Loaded 16163 players
   ✓ Extracted 34 features
   ✓ Feature matrix shape: (16163, 34)

[🤖] Training Male Players model...
Computing similarity matrix...
Similarity matrix computed: (16163, 16163)
   ✓ Similarity matrix computed: (16163, 16163)

[💾] Saving Male Players model...
Model saved to models/male_model.pkl
   ✓ Model saved: models/male_model.pkl
   ✓ File size: 1007.2 MB

[🧪] Testing Male Players model...
   ✓ Top player: Kylian Mbappé
   ✓ Search test: Found 5 players
   ✓ Recommendation test: 3 similar players found

✅ Male Players model trained successfully in 28.3s

======================================================================
  🟣 Training Female Players Model
======================================================================

[📊] Processing Female Players data...
   ✓ Loaded 1578 players
   ✓ Extracted 34 features
   ✓ Feature matrix shape: (1578, 34)

[🤖] Training Female Players model...
Computing similarity matrix...
Similarity matrix computed: (1578, 1578)
   ✓ Similarity matrix computed: (1578, 1578)

[💾] Saving Female Players model...
Model saved to models/female_model.pkl
   ✓ Model saved: models/female_model.pkl
   ✓ File size: 9.6 MB

[🧪] Testing Female Players model...
   ✓ Top player: Aitana Bonmatí
   ✓ Search test: Found 5 players
   ✓ Recommendation test: 3 similar players found

✅ Female Players model trained successfully in 1.9s

======================================================================
  📊 Training Summary
======================================================================

Models trained:
  ✅ Male Players Model   - 28.3s
  ✅ Female Players Model - 1.9s

Total training time: 30.2s

✨ You can now run the application:
   python run.py

   Or:
   cd app && python main.py

======================================================================
```

---

## System Requirements

### Minimum

- **CPU:** 2 cores
- **RAM:** 3 GB (male model requires ~2 GB during training)
- **Storage:** 3 GB free space
- **Python:** 3.8 or higher
- **Time:** ~30-40 seconds

### Recommended

- **CPU:** 4+ cores
- **RAM:** 4-8 GB
- **Storage:** 5 GB free (SSD preferred)
- **Python:** 3.9 or higher
- **Time:** ~20-30 seconds

---

## Troubleshooting

### Error: "Data file not found"

**Cause:** CSV files are missing or in wrong location

**Solution:**
```bash
# Check if files exist
ls new-data/
# Should show: male_players.csv, female_players.csv

# If missing, ensure you're in the project root directory
cd FIFA-Player-Recomendation
```

### Error: "Memory Error" or "Killed"

**Cause:** Insufficient RAM (especially for male model)

**Solutions:**
1. Close other applications to free up memory
2. Train female model only (smaller): `python training/train.py --female`
3. Use a machine with more RAM (recommended: 4GB+)
4. Train on cloud (Google Colab, AWS)

### Error: "Module not found"

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### Training is Very Slow

**Normal behavior:**
- Male model: 25-35 seconds (16K players)
- Female model: 1-3 seconds (1.5K players)

**If significantly slower:**
- Check CPU usage (should be ~100% during training)
- Use SSD instead of HDD
- Close background applications
- Ensure sufficient RAM available

### Model File Size is Large

**This is expected:**
- Male model: ~1 GB (contains 16K×16K similarity matrix)
- Female model: ~10 MB (contains 1.5K×1.5K similarity matrix)

**Why so large?**
- Precomputed similarity matrix enables fast recommendations (< 50ms)
- Trade-off: More disk space for faster inference
- This is a design choice for optimal performance

---

## Advanced Usage

### Training in Python Script

```python
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.data_processing import DataProcessor
from src.model import PlayerRecommender

# Process data
processor = DataProcessor()
processed = processor.process_for_training('new-data/male_players.csv')

# Train model
model = PlayerRecommender()
model.fit(
    data=processed['data'],
    normalized_features=processed['normalized_features'],
    feature_names=processed['feature_names']
)

# Save model
model.save('models/male_model.pkl')

# Use model
recommendations = model.recommend_similar('Kylian Mbappé', n_recommendations=10)
print(f"Found {len(recommendations)} similar players")
```

### Automated Training (CI/CD)

For automated training in CI/CD pipelines:

```bash
# Non-interactive mode
python training/train.py > training.log 2>&1

# Check exit code
if [ $? -eq 0 ]; then
    echo "Training successful"
else
    echo "Training failed"
    exit 1
fi
```

### Cloud Training

#### Google Colab

```python
# Clone repository
!git clone https://github.com/inboxpraveen/FIFA-Player-Recomendation.git
%cd FIFA-Player-Recomendation

# Install dependencies
!pip install -r requirements.txt

# Train models
!python training/train.py

# Download trained models
from google.colab import files
files.download('models/male_model.pkl')
files.download('models/female_model.pkl')
```

#### AWS EC2

```bash
# SSH into instance
ssh -i key.pem ubuntu@ec2-instance

# Clone and train
git clone https://github.com/inboxpraveen/FIFA-Player-Recomendation.git
cd FIFA-Player-Recomendation
pip install -r requirements.txt
python training/train.py
```

---

## Understanding the Algorithm

### Content-Based Filtering

The system uses **content-based filtering** with **cosine similarity**:

1. **Feature Extraction:** Extract 34 numerical attributes for each player
2. **Normalization:** Scale all features to 0-1 range
3. **Similarity Computation:** Calculate cosine similarity between all player pairs
4. **Precomputation:** Store similarity matrix for fast lookups

### Why Cosine Similarity?

```
similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**Advantages:**
- Scale-invariant (focuses on playing style, not absolute values)
- Fast to compute with vectorization
- Works well in high-dimensional spaces
- Range: 0 (different) to 1 (identical)

### Time Complexity

- **Training:** O(n²·d) where n=players, d=features (34)
- **Recommendation:** O(n) with precomputation (just lookup + filter)
- **Without precomputation:** O(n·d) per query (much slower)

**Result:** < 50ms recommendations instead of ~500ms

---

## Re-training

### When to Re-train

- ✅ New player data available (FC 26, etc.)
- ✅ Dataset updated with transfers
- ✅ Algorithm improvements
- ✅ Different feature weights needed

### How to Re-train

```bash
# Simply run the training script again
python training/train.py

# Old models will be overwritten
```

---

## Verification

After training, verify models exist and work:

```bash
# Check files
ls -lh models/
# Should show: male_model.pkl (~1GB), female_model.pkl (~10MB)

# Test models by running the app
python run.py

# Access in browser
# http://localhost:5000
```

---

## Next Steps

1. ✅ **Verify models exist:** `ls models/`
2. ✅ **Run the application:** `python run.py`
3. ✅ **Test features:** Search, recommend, compare players
4. ✅ **Switch genders:** Toggle between male/female datasets

---

## Getting Help

**Issues during training?**

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Ensure you meet [System Requirements](#system-requirements)
3. Verify dependencies: `pip install -r requirements.txt`
4. Check [GitHub Issues](https://github.com/inboxpraveen/FIFA-Player-Recomendation/issues)

**Still stuck?** Open a new issue with:
- Your OS and Python version
- Full error message
- Steps to reproduce

---

**Made with ⚽ by [Praveen Kumar](https://github.com/inboxpraveen)**

