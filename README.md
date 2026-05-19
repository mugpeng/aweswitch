<div align="center">
  <h1>aweswitch: Agent Profile Switcher</h1>
  <p><strong>A tiny local launcher for switching AI agent runtime profiles.</strong></p>
  <p>Keep provider URLs, tokens, and model names in one config file, then start an agent with the profile you choose.</p>
  <p>
    <strong>English</strong> ·
    <a href="./README_cn.md">简体中文</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/version-0.1.0-7C3AED?style=flat-square" alt="Version">
    <img src="https://img.shields.io/badge/python-%E2%89%A53.9-0EA5E9?style=flat-square" alt="Python">
    <img src="https://img.shields.io/badge/license-MPL--2.0-22C55E?style=flat-square" alt="License">
  </p>
  <p>
    <img src="https://img.shields.io/badge/status-alpha-c96a3d?style=flat-square" alt="Status">
    <img src="https://img.shields.io/badge/provider-Claude_Code-7C3AED?style=flat-square" alt="Claude Code">
    <img src="https://img.shields.io/badge/install-pip-22C55E?style=flat-square" alt="pip install">
    <img src="https://img.shields.io/badge/platform-local_CLI-334155?style=flat-square" alt="Local CLI">
  </p>
</div>

> Switch agent runtime profiles without rewriting the agent's own settings file.

`aweswitch` reads profiles from `~/.config/aweswitch/config.json`, expands environment references, prepares provider-specific runtime arguments, and then starts the selected agent.

It is intentionally small. The project is positioned as an agent profile switcher, but today it supports Claude Code profiles only. Codex and Hermes profile groups may appear in the config shape later, but they are not executable yet.

## Install

Install from PyPI:

```bash
python3 -m pip install aweswitch
aweswitch --help
```

Create the default config:

```bash
aweswitch config init
```

Then open the config and align it with your real Claude Code providers, models, and token variable names:

```bash
aweswitch config edit
```

The default config shape groups profiles under their provider. This is a reference config you can adapt:

```json
{
  "profiles": {
    "claude": {
      "cc-glm": {
        "env": {
          "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
          "ANTHROPIC_AUTH_TOKEN": "${GLM_ANTHROPIC_AUTH_TOKEN}",
          "ANTHROPIC_MODEL": "glm-5.1"
        }
      },
      "cc-gemini": {
        "env": {
          "ANTHROPIC_BASE_URL": "https://openclaw.chatgo.best",
          "ANTHROPIC_AUTH_TOKEN": "${GEMINI_ANTHROPIC_AUTH_TOKEN}",
          "ANTHROPIC_MODEL": "gemini-3.1-pro-preview"
        }
      },
      "cc-xiaomi": {
        "env": {
          "ANTHROPIC_BASE_URL": "https://token-plan-sgp.xiaomimimo.com/anthropic",
          "ANTHROPIC_AUTH_TOKEN": "${XIAOMI_ANTHROPIC_AUTH_TOKEN}",
          "ANTHROPIC_MODEL": "mimo-v2.5-pro"
        }
      }
    }
  }
}
```

Configure the token variables referenced by your profiles:

```bash
export GLM_ANTHROPIC_AUTH_TOKEN="..."
export GEMINI_ANTHROPIC_AUTH_TOKEN="..."
export XIAOMI_ANTHROPIC_AUTH_TOKEN="..."
```

Put long-lived variables in `~/.zshrc` if you want them available in every shell.

Verify the configured profiles:

```bash
aweswitch list
aweswitch show cc-glm
```

Run a profile:

```bash
aweswitch cc-glm
```

Pass extra arguments through to Claude Code:

```bash
aweswitch cc-glm --dangerously-skip-permissions
```

Useful config commands:

```bash
aweswitch config path
aweswitch config show
aweswitch config edit
```

## FAQ

### Why aweswitch, and who is it for?

`aweswitch` is for people who use AI coding agents with more than one runtime endpoint, model, or token source and want a repeatable local command instead of editing settings by hand.

- **One local config file** at `~/.config/aweswitch/config.json`
- **Named agent profiles** such as `cc-glm`, `cc-gemini`, or `cc-xiaomi`
- **Runtime-only injection** through provider-specific arguments
- **No mutation of the agent's original settings file**
- **Token references** through shell variables or `~/.claude/settings.json`
- **Readable JSON** with provider grouping under `profiles.claude`

### Where does aweswitch store profiles?

By default, profiles live in:

```bash
~/.config/aweswitch/config.json
```

You can override that path with `AWESWITCH_CONFIG`.

### Does aweswitch modify Claude settings?

No. It reads your aweswitch config and launches Claude Code with runtime settings for that process only.

### Does aweswitch support Codex or Hermes?

Not yet. The config format groups profiles by provider so future support can fit naturally, but the executable provider set is currently Claude Code only.

## Similar Tools

### [cc-switch](https://github.com/farion1231/cc-switch)

`cc-switch` is an adjacent Claude Code switching tool. It is useful reference material for the same problem space: making Claude Code provider/model switching easier from the command line.

`aweswitch` currently takes a smaller Python-package approach: a local JSON profile file, runtime-only Claude Code `--settings`, secret redaction for inspection commands, and provider grouping that leaves room for future agent support.

## Profile Rules

- Profiles are grouped under `profiles.<provider>.<profileName>`.
- `claude` is the only supported provider right now.
- Profile names must be unique across all provider groups.
- Claude profiles pass `env` through runtime `--settings '{"env": ...}'`.
- Set the Claude model with `env.ANTHROPIC_MODEL`.
- `env` values only apply to the launched process.
- `${VAR_NAME}` values are expanded from the current shell environment.
- Claude token values can also expand from `~/.claude/settings.json` when they are missing from the shell.
- `show` and `config show` redact keys matching token, key, secret, password, or auth.

## Claude Model Overrides

For Claude profiles, `ANTHROPIC_MODEL` is the primary model setting.

`ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, and `ANTHROPIC_DEFAULT_OPUS_MODEL` are not configured by default.

If you want Claude Code to use a lighter model for lightweight or background tasks, add `ANTHROPIC_DEFAULT_HAIKU_MODEL` to the profile:

```json
{
  "profiles": {
    "claude": {
      "cc-xiaomi": {
        "env": {
          "ANTHROPIC_BASE_URL": "https://token-plan-sgp.xiaomimimo.com/anthropic",
          "ANTHROPIC_AUTH_TOKEN": "${XIAOMI_ANTHROPIC_AUTH_TOKEN}",
          "ANTHROPIC_MODEL": "mimo-v2.5-pro",
          "ANTHROPIC_DEFAULT_HAIKU_MODEL": "mimo-v2.5"
        }
      }
    }
  }
}
```

This keeps the main model on `mimo-v2.5-pro` while allowing Claude Code to use `mimo-v2.5` for lighter work.

## Development

Run the test suite:

```bash
python3 tests/test_aweswitch.py
```

Run the syntax check:

```bash
python3 -m py_compile aweswitch.py src/aweswitch/cli.py tests/test_aweswitch.py
```

Install the local checkout in editable mode:

```bash
python3 -m pip install -e .
```

Build a local package:

```bash
python3 -m pip install build
python3 -m build
```

Install a built wheel locally:

```bash
python3 -m pip install dist/aweswitch-0.1.0-py3-none-any.whl
```

Project docs:

- [Contributing](./docs/CONTRIBUTING.md)
- [Changelog](./docs/CHANGELOG.md)
