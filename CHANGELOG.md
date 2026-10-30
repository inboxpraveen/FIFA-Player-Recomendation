# Changelog

All notable changes to the FIFA Player Recommendation System.

## [2.1.0] - 2026-10-30

Smaller, faster and ready to deploy. Retrain once with `python training/train.py`; 2.0 model files still load in the meantime.

### Changed

- **Similarity is computed on demand.** The precomputed n x n matrix is gone. The men's model shrinks from 1.97 GB to 1.9 MB, a recommendation drops from about 2.2 s to about 5 ms, and training both models takes 0.5 s instead of 5.7 s.
- **Attributes are standardized (z-scores) instead of min-max scaled.** Cosine scores on min-max data all sat between 99% and 100%. Standardized features separate roles and quality: for Rodri the top five are now Locatelli, Merino, Tchouaméni, Rice and Guimarães.
- **Partial name matches pick the highest rated player** instead of the first row that matched.
- `recommend_by_attributes` scales its target with the training mean and std, so custom searches are consistent with player-to-player results.
- Feature count corrected to 35 in all documentation (it was listed as 34).
- Dependencies trimmed to what the code uses: scikit-learn, SciPy and python-dotenv are no longer required. Python 3.11+ is required by pandas 3.

### Added

- `Dockerfile`: trains during the build, runs gunicorn as a non-root user, with a health check.
- `GET /api/health`, returning `503` until both models are loaded.
- A pytest suite for the model and every endpoint.
- `SECURITY.md`, a new logo, banner, social preview image and architecture diagram.
- `HOST`, `PORT` and `MODELS_DIR` environment variables.

### Fixed

- The app now works under gunicorn and other WSGI servers. Models previously loaded only when started through `run.py`.
- Model paths resolve from the project root, so the app and training script work from any directory.
- After `pip install -e .`, the `fifa-recommender` command starts the app from any directory: `run.py` now has the `main()` it pointed to.
- Training no longer crashes on Windows when its output is redirected to a file, and `--male` or `--female` no longer reports the other model as failed.
- Search, team, nation and league filters treat input as text, so characters like `(` no longer cause errors.
- Client-supplied sizes are bounded, malformed JSON returns `400`, and `500` responses no longer include exception details.
- The development server listens on `127.0.0.1` by default and debug mode is off unless `FLASK_DEBUG=1`.

## [2.0.0] - 2025-12-17

### Major Revamp

Complete project overhaul with modern architecture, new UI, and improved recommendation system.

### Added

- **Dual Gender Models** - Separate male and female player recommendation systems
- **Modern Glassmorphism UI** - Beautiful light theme with transparent effects
- **Player Comparison** - Compare up to 4 players with interactive radar charts
- **Advanced Search** - Filter by position, rating, nation, league, team
- **Gender Toggle** - Easy switch between male/female datasets
- **Training Script** - Simple Python script (`training/train.py`) for model training
- **Comprehensive Documentation** - README, Installation Guide, Training Guide, Technical Docs

### Improved

- **Performance** - 10x faster recommendations with precomputed similarity matrices
- **Architecture** - Industry-standard structure with clean separation of concerns
- **Algorithm** - Content-based filtering with cosine similarity on 34 attributes
- **Data Processing** - Automated cleaning, normalization, and feature extraction
- **Error Handling** - Graceful error messages and validation

### Project Structure

```
FIFA-Player-Recomendation/
├── app/              # Flask web application
├── src/              # Core recommendation engine
├── training/         # Model training (NEW)
├── models/           # Trained models (generated)
├── new-data/         # FC 25 datasets
└── [documentation files]
```

### Removed

- Old Jupyter notebooks (replaced with Python training script)
- Old analysis HTML pages
- Old assets and static files
- Redundant documentation files

### Performance

- Search: ~45ms (< 100ms target)
- Recommendations: ~30ms (< 50ms target)
- Comparison: ~15ms
- Accuracy: ~94% similarity matching

### Technology Stack

- **Backend:** Flask 3.0
- **ML/AI:** scikit-learn, NumPy, Pandas
- **Frontend:** Vanilla JavaScript, CSS3
- **Charts:** Chart.js
- **Dataset:** FC 25 (~17.5K total players)

### Documentation

- README.md - Main documentation
- training/README.md - Complete training guide
- PROJECT_SUMMARY.md - Technical documentation
- INSTALL.md - Installation instructions
- CONTRIBUTING.md - Contribution guidelines

---

## [1.0.0] - Previous Version

Initial release with basic recommendation features.

