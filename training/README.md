# Model Training Guide

`training/train.py` turns the player CSVs in `new-data/` into the two model files the app serves.

```bash
python training/train.py
```

Both models are built and written to `models/` in about half a second.

## Options

```bash
python training/train.py                # both models (default)
python training/train.py --male         # men's model only
python training/train.py --female       # women's model only
python training/train.py --skip-male    # everything except the men's model
python training/train.py --skip-female  # everything except the women's model
```

The script exits with status 1 if any requested model fails, so it can be used in scripts and Docker builds.

## What it produces

| File | Players | Features | Training time | Size |
|------|---------|----------|---------------|------|
| `models/male_model.pkl` | 16,034 | 35 | 0.4 s | 1.9 MB |
| `models/female_model.pkl` | 1,575 | 35 | 0.1 s | 0.2 MB |

Measured on an Intel Core i7-14650HX laptop. Any machine that can run pandas will do; training needs well under 1 GB of RAM.

## What happens

For each dataset the script:

1. **Loads** the CSV and drops the unnamed index columns.
2. **Cleans** it: drops rows missing a rating or attribute, fills display fields, removes duplicate names and adds a position group (Goalkeeper, Defender, Midfielder, Forward).
3. **Extracts** 35 numeric attributes: the six face stats and 29 detailed attributes.
4. **Standardizes** each attribute to zero mean and unit variance, keeping the mean and std.
5. **Saves** the player table, the float32 feature matrix and the scaling statistics with joblib.
6. **Smoke-tests** the saved model: finds the top player, runs a search and asks for three recommendations.

There is no similarity matrix to build. The app computes cosine similarity for one player against all others when a request comes in, which takes about 5 ms. [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md#recommendation-algorithm) explains the algorithm and why the attributes are standardized.

## Sample output

```
======================================================================
  Training Male Players Model
======================================================================

[1] Processing Male Players data...
Cleaned data: 16034 players remaining
   - Loaded 16034 players
   - Extracted 35 features
   - Feature matrix shape: (16034, 35)

[2] Training Male Players model...
   - Indexed 16034 players for on-demand cosine similarity

[3] Saving Male Players model...
Model saved to .../models/male_model.pkl
   - Model saved: .../models/male_model.pkl
   - File size: 1.9 MB

[4] Testing Male Players model...
   - Top player: Kylian Mbappé
   - Search test: Found 5 players
   - Recommendation test: 3 similar players found

Male Players model trained successfully in 0.4s
```

Output is plain ASCII apart from player names, so it can be piped to a log file on any platform.

## Using a new dataset

Replace `new-data/male_players.csv` and `new-data/female_players.csv` with files that have the same column names (for example, a later FC release scraped in the same format) and run the script again. Old model files are overwritten. Restart the app, or the gunicorn workers, to load them.

The columns the pipeline needs are `Name`, `OVR`, `Position`, `Age`, `Nation`, `League`, `Team`, `Height`, `Weight`, `Preferred foot`, `Weak foot`, `Skill moves` and the 35 attributes listed in `DataProcessor.FEATURE_COLUMNS` in `src/data_processing.py`.

## Training from Python

```python
from src.data_processing import DataProcessor
from src.model import PlayerRecommender

processed = DataProcessor().process_for_training("new-data/female_players.csv")

model = PlayerRecommender()
model.fit(
    data=processed["data"],
    normalized_features=processed["normalized_features"],
    feature_names=processed["feature_names"],
    feature_mean=processed["feature_mean"],
    feature_std=processed["feature_std"],
)
model.save("models/female_model.pkl")

print(model.recommend_similar("Sam Kerr", n_recommendations=5))
```

## Models from version 2.0

Version 2.0 stored a full n x n similarity matrix, which made the men's model about 2 GB. Those files still load: the matrix is ignored and the features are re-standardized in memory, and the app prints a reminder. Run the training script once to replace them with the small format.

## Troubleshooting

**`Data file not found`**: the CSVs must be at `new-data/male_players.csv` and `new-data/female_players.csv`. The script resolves paths from the project root, so it can be run from any directory.

**`ModuleNotFoundError`**: install the dependencies in the active environment with `pip install -r requirements.txt`.

**`KeyError` on a column name**: the CSV does not have the expected columns. Compare its header with the list above.

**The app still shows old results**: restart it. Models are loaded once at startup.
