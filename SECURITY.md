# Security policy

## Supported versions

Security fixes go into the latest release on `main`. Older releases are not patched.

## Reporting a vulnerability

Please report security issues privately, not in a public issue.

Open the repository's **Security** tab and choose **Report a vulnerability**. This creates a private advisory visible only to the maintainer.

Include what you found, the steps to reproduce it, and the version or commit you tested. You can expect an acknowledgement within a week. Once a fix is released, the report can be disclosed publicly with credit if you want it.

## Deployment notes

- **Model files are Python pickles.** `models/*.pkl` are written with joblib, and loading a pickle can run code. Only load model files you trained yourself or received from a source you fully trust. Never point `MODELS_DIR` at a directory other people can write to.
- **Do not expose the development server.** `python run.py` listens on `127.0.0.1` by default. For anything public, use gunicorn, waitress or the Docker image, and never set `FLASK_DEBUG=1`.
- **Serve over HTTPS** behind a reverse proxy or your platform's load balancer.
- **The API has no authentication or rate limiting.** Every request is bounded (at most 100 results, 4 players per comparison, 20 suggestions), but if you expose it publicly, add rate limiting at the proxy.
- **Errors are not leaked.** Unexpected failures return a generic `500`; the details go to the server log only.
- **The Docker image runs as a non-root user.**
