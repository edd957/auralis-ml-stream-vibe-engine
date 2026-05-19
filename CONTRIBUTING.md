# Contributing

Thanks for helping improve Auralis ML.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Install optional extras only when working on those areas:

```bash
pip install -e ".[ml,audio,chat]"
```

## Pull Request Guidelines

- Keep changes focused and documented.
- Include tests for policy, scoring, API, or FFmpeg behavior changes.
- Avoid committing model weights, generated audio, credentials, or local `.env` files.
- Use clear English commit messages and PR descriptions.

