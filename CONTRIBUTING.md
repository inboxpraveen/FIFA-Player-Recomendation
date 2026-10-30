# Contributing

Thanks for your interest in improving the FIFA Player Recommendation System. Bug reports, fixes, new features and documentation are all welcome.

## Getting started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/FIFA-Player-Recomendation.git
   cd FIFA-Player-Recomendation
   ```
2. Create a branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development setup

```bash
conda create -n fifa-rec python=3.12 -y    # or: python -m venv .venv
conda activate fifa-rec
pip install -r requirements.txt pytest
python training/train.py
python run.py
```

The app runs at http://localhost:5000.

## Tests

```bash
python -m pytest
```

The suite trains on the women's dataset in memory, so it runs in about a second and does not need `models/`. Add or update tests for any change to `src/` or `app/main.py`. For UI changes, check both themes, both datasets and a narrow mobile viewport, and keep the browser console free of errors.

## Coding standards

**Python**
- Follow PEP 8 and match the style of the surrounding code.
- Use type hints and docstrings on public functions.
- Keep heavy work out of the request path. Anything per-player belongs in training or in vectorized NumPy, not in a Python loop over rows.
- Never return exception text to API clients; use `server_error()` in `app/main.py`.

**JavaScript and CSS**
- Plain ES6+, no build step.
- Insert user-visible text with `textContent`, not `innerHTML`, unless the content is from the dataset.
- Use the CSS variables for colours so both themes keep working.

## Pull requests

1. Keep each pull request focused on one change.
2. Describe what changed and why, and link the related issue.
3. Add screenshots for UI changes.
4. Update the README or other docs if behaviour, the API or measured figures change.

**Checklist**

- [ ] `python -m pytest` passes
- [ ] Works with both the men's and women's datasets
- [ ] Docs updated where needed
- [ ] No new dependencies unless they are clearly needed

## Reporting bugs and requesting features

Open a [GitHub issue](https://github.com/inboxpraveen/FIFA-Player-Recomendation/issues) with steps to reproduce, expected and actual behaviour, and your OS and Python version. For feature requests, describe the use case first.

Security problems should be reported privately. See [SECURITY.md](SECURITY.md).

## Good places to start

- Use the goalkeeper attributes (`GK Diving`, `GK Handling` and others) when comparing goalkeepers
- Per-role attribute weights, for example favouring defending attributes for centre-backs
- A name matcher that handles accents and duplicate names better
- Support for newer FC datasets
- Translations of the UI

## Code of conduct

Be respectful, assume good intent, and keep feedback constructive. Newcomers are welcome.
