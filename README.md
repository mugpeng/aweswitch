# aweswitch

`aweswitch` is a small launcher for switching Claude Code and Codex runtime profiles.

It reads profiles from `~/.config/aweswitch/config.json`, applies profile-specific environment variables or runtime flags, and then starts the selected agent. It does not modify the original Claude or Codex config files.

## Install

Copy the script into a directory on your `PATH`:

```bash
cp aweswitch.py ~/.local/bin/aweswitch
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
aweswitch codex-mini
```

Extra arguments are passed through to the underlying agent:

```bash
aweswitch cc-glm --dangerously-skip-permissions
aweswitch codex-mini --cd /path/to/project
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
    "cc-glm": {
      "provider": "claude",
      "model": "glm-5.1",
      "env": {
        "ANTHROPIC_BASE_URL": "${ANTHROPIC_BASE_URL}",
        "ANTHROPIC_AUTH_TOKEN": "${ANTHROPIC_AUTH_TOKEN}",
        "ANTHROPIC_MODEL": "glm-5.1",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-5.1",
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.1",
        "ANTHROPIC_REASONING_MODEL": "glm-5.1"
      }
    },
    "codex-mini": {
      "provider": "codex",
      "model": "gpt-5.4-mini",
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}"
      }
    }
  }
}
```

## Profile Rules

- `provider: "claude"` runs `claude`.
- `provider: "codex"` runs `codex`.
- `model` for Claude sets `ANTHROPIC_MODEL` at runtime, unless `env.ANTHROPIC_MODEL` is explicitly set in the profile.
- `model` for Codex is passed as `--model <model>`.
- `env` values only apply to the launched process.
- `${VAR_NAME}` values are expanded from your current shell environment.
- Claude profiles can also expand `${ANTHROPIC_*}` values from `~/.claude/settings.json` when they are not set in the shell.

## Environment Variables

For custom providers, define the variables referenced by your profile:

```bash
export ANTHROPIC_BASE_URL="..."
export ANTHROPIC_AUTH_TOKEN="..."
```

Put long-lived variables in `~/.zshrc` if you want them available in every shell.

## Testing

Run:

```bash
python3 tests/test_aweswitch.py
```
