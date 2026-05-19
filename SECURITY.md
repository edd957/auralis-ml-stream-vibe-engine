# Security Policy

## Supported Versions

Auralis ML is currently pre-1.0. Security fixes are applied to the latest version on the
`main` branch.

## Reporting a Vulnerability

Please open a private security advisory on GitHub or contact the maintainers with a
minimal reproduction, affected version, and expected impact. Do not publish exploit
details until a fix is available.

## Runtime Notes

- Never commit real Twitch, YouTube, Redis, or model-provider credentials.
- Treat FFmpeg input paths as trusted operator input only.
- Keep optional ML and chat dependencies updated in production deployments.
