# Contributing

Thanks for helping with aichs. Small fixes, weird ideas, extensions, docs, and
sharp opinions are all welcome.

## Development Setup

For local development, run the app from source:

```bash
git clone https://github.com/nadav-yo/aichs
cd aichs
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python main.py
```

API keys can be configured in **Settings -> Models** or through environment
variables. Requires Python 3.11+.

Project agent instructions live in [AGENTS.md](AGENTS.md).

## Package Installs

For normal use, prefer `pipx`:

```bash
pipx install aichs
pipx upgrade aichs
```

If you use `pip` instead of `pipx`, install or upgrade with:

```bash
python -m pip install --user aichs
python -m pip install --user --upgrade aichs
```

On Windows, make sure Python's user script directory is on `PATH`, for example
`C:\Users\<you>\AppData\Roaming\Python\Python311\Scripts`.

## Tests

Run the full suite from the repository root:

```bash
pytest -q --cov-fail-under=90
```

Single-file test runs are useful while iterating, but they do not represent the
real coverage number because coverage is measured across the configured package
set. For a quick local check without coverage:

```bash
pytest --no-cov
```

## Packaging

For a distributable desktop build, use PyInstaller:

```bash
python tools/build_package.py
```

Outputs are written under `dist/`:

| OS | Output |
|---|---|
| Windows | `dist/aichs/aichs.exe` |
| macOS | `dist/aichs.app` and `dist/aichs/` |
| Linux | `dist/aichs/aichs` |

Build on each target OS for that OS; PyInstaller is not a cross-compiler.

## Publishing

To publish a release, run the **release** GitHub Actions workflow from the
branch you want to release with a version such as `0.2.1`. It runs the test
suite, updates `pyproject.toml`, commits `Release version 0.2.1`, tags that
commit as `v0.2.1`, and pushes the commit and tag.

The **publish** workflow only runs for `v*` tags. It checks out the tag, builds
the distributions, verifies the filenames match the tag version, and uploads to
PyPI with Trusted Publishing.
