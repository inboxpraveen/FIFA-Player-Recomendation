# Installation Guide

## Requirements

- Python 3.11 or newer
- About 300 MB of disk space for the dependencies
- Any operating system: Windows, macOS or Linux

Docker is an alternative that needs no local Python.

## 1. Get the code

```bash
git clone https://github.com/inboxpraveen/FIFA-Player-Recomendation.git
cd FIFA-Player-Recomendation
```

## 2. Create an environment

**conda**

```bash
conda create -n fifa-rec python=3.12 -y
conda activate fifa-rec
```

**venv**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, pandas, NumPy, joblib and gunicorn, pinned to tested versions.

## 4. Train the models

```bash
python training/train.py
```

This writes `models/male_model.pkl` (1.9 MB) and `models/female_model.pkl` (0.2 MB) in about half a second. See [training/README.md](training/README.md) for options.

## 5. Run the app

```bash
python run.py
```

Open http://localhost:5000. To listen on another port or on all interfaces:

```bash
PORT=8080 HOST=0.0.0.0 python run.py               # macOS / Linux
$env:PORT=8080; $env:HOST="0.0.0.0"; python run.py # Windows PowerShell
```

## Verify

```bash
curl http://localhost:5000/api/health
# {"models":{"female":true,"male":true},"status":"ok"}

pip install pytest
python -m pytest
```

## Docker

```bash
docker build -t fifa-player-rec .
docker run -d -p 8000:8000 --name fifa-player-rec fifa-player-rec
```

The image trains the models during the build and serves them with gunicorn on port 8000 as a non-root user. Open http://localhost:8000.

## Production

Use a WSGI server instead of `python run.py`:

```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 app.main:app      # Linux / macOS
waitress-serve --port=8000 app.main:app                    # Windows (pip install waitress)
```

Each worker uses about 115 MB of memory. Serve it behind HTTPS and read [SECURITY.md](SECURITY.md) first.

## Troubleshooting

**"Models not found!"**: run `python training/train.py` first. If your models live elsewhere, set `MODELS_DIR`.

**`/api/health` returns 503**: one of the model files is missing or unreadable. The server log says which.

**`ModuleNotFoundError`**: the environment with the dependencies is not active. Activate it and run `pip install -r requirements.txt` again.

**Port 5000 is in use** (common on macOS, where AirPlay uses it): start with `PORT=5001 python run.py`.

**pandas fails to install**: pandas 3 needs Python 3.11 or newer. Check with `python --version`.

**Accented names look wrong in the terminal on Windows**: this is the console encoding, not the data. Set `PYTHONIOENCODING=utf-8` or use Windows Terminal. The web app is unaffected.

## Uninstall

```bash
conda env remove -n fifa-rec     # or delete the .venv folder
docker rmi fifa-player-rec       # if you built the image
```

Then delete the project folder.
