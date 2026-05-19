# aweswitch

`aweswitch` is a small launcher for switching Claude Code runtime profiles.

It reads profiles from `~/.config/aweswitch/config.json`, applies profile-specific environment variables, and then starts Claude Code. It does not modify the original Claude config file.

## Install

Copy the script into a directory on your `PATH`:

```bash
cp aweswitch.py ~/.local/bin/aweswitch
cp default-config.json ~/.local/bin/default-config.json
chmod +x ~/.local/bin/aweswitch
```

Make sure `~/.local/bin` is on your `PATH`:

```bash
echo $PATH
```

If it is missing, add this to `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell:

```bash
source ~/.zshrc
```

## Quick Start

Create the default config:

```bash
aweswitch config init
```

List profiles:

```bash
aweswitch list
```

Show one profile:

```bash
aweswitch show cc-glm
```

Run a profile:

```bash
aweswitch cc-glm
```

Extra arguments are passed through to the underlying agent:

```bash
aweswitch cc-glm --dangerously-skip-permissions
```

## Config

The default config path is:

```bash
~/.config/aweswitch/config.json
```

You can inspect or edit it with:

```bash
aweswitch config path
aweswitch config show
aweswitch config edit
```

Example:

```json
{
  "profiles": {
    "claude": {
      "cc-glm": {
        "env": {
          "ANTHROPIC_BASE_URL": "https://glm-provider.example.com/api/anthropic",
          "ANTHROPIC_AUTH_TOKEN": "${ANTHROPIC_AUTH_TOKEN}",
          "ANTHROPIC_MODEL": "glm-5.1"
        }
      }
    }
  }
}
```

## Profile Rules

- Profiles are grouped under `profiles.claude`.
- Profile names must be unique across all provider groups.
- Claude profiles pass `env` through runtime `--settings '{"env": ...}'`, matching Claude Code's native settings mechanism. Set the Claude model with `env.ANTHROPIC_MODEL`.
- `env` values only apply to the launched process.
- `${VAR_NAME}` values are expanded from your current shell environment.
- Claude profiles can also expand token variables such as `${ANTHROPIC_AUTH_TOKEN}` from `~/.claude/settings.json` when they are not set in the shell.
- Codex and Hermes profiles are not supported yet.

## Claude Model Overrides

For Claude profiles, `ANTHROPIC_MODEL` is the primary model setting.

`ANTHROPIC_DEFAULT_HAIKU_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL`, and
`ANTHROPIC_DEFAULT_OPUS_MODEL` are not configured by default.

If you want Claude Code to use a lighter model for lightweight or background
tasks, you can manually add `ANTHROPIC_DEFAULT_HAIKU_MODEL` to
`~/.config/aweswitch/config.json`. You can inspect or edit that file with:

```bash
aweswitch config path
aweswitch config show
aweswitch config edit
```

Example:

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

This keeps the main model on `mimo-v2.5-pro` while allowing Claude Code to use
`mimo-v2.5` for lighter or background functionality.

## Environment Variables

Before running a profile, configure the token environment variables referenced by that profile:

```bash
export ANTHROPIC_AUTH_TOKEN="..."
export GEMINI_ANTHROPIC_AUTH_TOKEN="..."
export XIAOMI_ANTHROPIC_AUTH_TOKEN="..."
```

Put long-lived variables in `~/.zshrc` if you want them available in every shell.

## Testing

Run:

```bash
python3 tests/test_aweswitch.py
```
