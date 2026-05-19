# change log

## v0.1.0

`v0.1.0` is the first package-oriented release line for aweswitch. The project now installs as a Python package with a console-script entry point, while keeping the CLI intentionally small and dependency-free at runtime.

### Python package installation

aweswitch now uses a `pyproject.toml` package definition with a `src/aweswitch/` layout. The command is exposed through the package entry point:

```toml
[project.scripts]
aweswitch = "aweswitch.cli:main"
```

The default config template is bundled as package data, so `aweswitch config init` works after `pip install aweswitch` without copying files by hand.

### Agent profile switcher positioning

The project positioning was broadened from a Claude Code-only profile switcher to an agent profile switcher. The executable provider set remains intentionally limited to Claude Code for now.

### Similar tools

The README now calls out [cc-switch](https://github.com/farion1231/cc-switch) as a similar Claude Code switching tool and explains how aweswitch currently differs: smaller Python package, local JSON profiles, runtime-only Claude Code `--settings`, and redacted inspection commands.

### Highlights

- Started versioning at `v0.1.0`
- Added `pyproject.toml`
- Moved implementation into `src/aweswitch/cli.py`
- Added the `aweswitch = "aweswitch.cli:main"` console script
- Bundled `default-config.json` as package data
- Updated README badges in the aweskill style
- Repositioned aweswitch as an agent profile switcher
- Added a similar-tools note for `cc-switch`

## dev

The `dev` branch now groups profiles under provider keys while keeping the command-line experience simple. Config files use `profiles.claude.<profileName>` instead of repeating `provider: "claude"` inside every profile. The executable provider set is intentionally limited to Claude Code for now, and Codex has been removed from the default configuration.

### Provider-grouped profiles

Profiles now live under provider groups:

```json
{
  "profiles": {
    "claude": {
      "cc-glm": {
        "env": {
          "ANTHROPIC_MODEL": "glm-5.1"
        }
      }
    }
  }
}
```

Profile names are still invoked directly with `aweswitch <profile>`, so existing command usage stays short. If a profile name appears under multiple providers, aweswitch reports it as ambiguous.

### Claude-only default config

The default config now contains only Claude Code profiles. Codex and Hermes are reserved for future provider support and are not executable in the current CLI.

### Documentation refresh

The README files were reworked around the same structure used by the larger aweskill project: concise positioning, install steps, FAQ, quick start, config rules, and development notes. Contributor guidance now lives in `docs/CONTRIBUTING.md`.

### Highlights

- Grouped config under `profiles.claude`
- Removed per-profile `provider` fields
- Removed `codex-mini` from the default config
- Kept direct `aweswitch <profile>` invocation
- Added duplicate profile-name detection
- Added contributor documentation
- Refreshed English and Chinese READMEs

## initial line

Earlier commits introduced the single-file Python launcher, externalized the default config template, added tests, inherited token values from Claude settings when needed, switched Claude profile env injection to runtime `--settings`, and documented Claude model override behavior.
