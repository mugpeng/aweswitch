# Contributing to aweswitch

`aweswitch` is intentionally small: a local agent profile launcher with a readable JSON config and a thin CLI.

The project should stay focused on that job. Prefer changes that make profile switching clearer, safer, or easier to maintain. Avoid turning it into a general agent manager or a broad configuration platform.

## Development Setup

Clone the repository and run the tests:

```bash
git clone https://github.com/mugpeng/aweswitch.git
cd aweswitch
python3 -m pip install -e .
python3 tests/test_aweswitch.py
python3 -m py_compile src/aweswitch/cli.py tests/test_aweswitch.py
```

For local CLI testing:

```bash
python3 -m pip install -e .
aweswitch --help
```

## Branches

The repository uses two long-lived branches:

- `main` is the stable line.
- `dev` is the integration branch for day-to-day development.

Do feature work on `dev` unless a maintainer says otherwise.

## Engineering Taste

Prefer solutions that are simple, clear, decoupled, honest, focused, and durable.

- Simple: make the smallest change that solves the real problem.
- Clear: optimize for the next reader, not for cleverness.
- Decoupled: keep boundaries clean, but do not add abstractions without a real need.
- Honest: make complexity, state, side effects, assumptions, and failure modes visible.
- Focused: preserve the small launcher model and keep top-level commands minimal.
- Durable: choose behavior that is easy to test and maintain.
- First principles: identify the real problem and hard constraints before adding concepts.

## Code Style

- Runtime language: Python 3.
- Package layout: `src/aweswitch/`.
- Keep the runtime dependency-free unless a dependency clearly earns its cost.
- Prefer small functions around config loading, profile resolution, argument preparation, and CLI commands.
- Keep user-facing errors actionable.
- Keep config examples valid JSON.
- Do not print raw secret values from `show` or `config show`.

## Config Semantics

The stable config shape is:

```json
{
  "profiles": {
    "claude": {
      "profile-name": {
        "env": {}
      }
    }
  }
}
```

Current rules:

- `claude` is the only executable provider.
- Profile names must be unique across provider groups.
- Claude profiles are passed through runtime `--settings`.
- Environment references use `${VAR_NAME}`.
- Shell environment values take precedence over values loaded from `~/.claude/settings.json`.

## Documentation

If you change command behavior, config shape, supported providers, or install steps, update the relevant docs in the same change:

- `README.md`
- `README_cn.md`
- `docs/CHANGELOG.md`
- tests that define the behavior

## Testing

Before committing, run:

```bash
python3 tests/test_aweswitch.py
python3 -m py_compile src/aweswitch/cli.py tests/test_aweswitch.py
```

If a change affects command output or config parsing, add or update tests in `tests/test_aweswitch.py`.

## Releasing

There is no automated release pipeline yet. Versioning starts at `v0.1.0`.

For now:

1. Update `docs/CHANGELOG.md`.
2. Commit the change on `dev`.
3. Merge `dev` into `main` when ready.
4. Build the package with `python3 -m build`.
5. Upload with `python3 -m twine upload dist/*` when publishing to PyPI.

## Questions

When in doubt, keep the change smaller. A focused fix or documentation improvement is better than a broad rewrite.
