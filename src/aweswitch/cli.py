#!/usr/bin/env python3
import copy
import json
import os
import re
import shlex
import shutil
import sys
from pathlib import Path


TEMPLATE_PATH = Path(__file__).parent / "default-config.json"

SECRET_RE = re.compile(r"(TOKEN|KEY|SECRET|PASSWORD|AUTH)", re.IGNORECASE)
ENV_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def config_path():
    return Path(os.environ.get("AWESWITCH_CONFIG", "~/.config/aweswitch/config.json")).expanduser()


def claude_settings_path():
    return Path(os.environ.get("CLAUDE_SETTINGS", "~/.claude/settings.json")).expanduser()


def die(message):
    raise SystemExit(f"aweswitch: {message}")


def init_config(path):
    path = Path(path).expanduser()
    if path.exists():
        die(f"config already exists: {path}")
    if not TEMPLATE_PATH.exists():
        die(f"template not found: {TEMPLATE_PATH}")
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_PATH, path)


def load_config(path):
    path = Path(path).expanduser()
    if not path.exists():
        die(f"config not found: {path}\nrun: aweswitch config init")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        die(f"invalid config JSON at {path}: {exc}")
    if not isinstance(data.get("profiles"), dict):
        die("config must contain a profiles object")
    return data


def load_claude_settings_env(path=None):
    path = claude_settings_path() if path is None else Path(path).expanduser()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    env = data.get("env", {})
    if not isinstance(env, dict):
        return {}
    return {key: value for key, value in env.items() if isinstance(value, str)}


def expand_value(value, env):
    if not isinstance(value, str):
        return value

    def replace(match):
        name = match.group(1)
        if name not in env:
            die(f"missing environment variable: {name}")
        return env[name]

    return ENV_REF_RE.sub(replace, value)


def profile_for(config, name):
    matches = []
    for provider, provider_profiles in config.get("profiles", {}).items():
        if not isinstance(provider_profiles, dict):
            die(f"provider profiles must be an object: {provider}")
        profile = provider_profiles.get(name)
        if profile is not None:
            matches.append((provider, profile))

    if not matches:
        die(f"unknown profile: {name}")
    if len(matches) > 1:
        die(f"ambiguous profile: {name}")

    provider, profile = matches[0]
    if not isinstance(profile, dict):
        die(f"profile must be an object: {provider}.{name}")
    return provider, profile


def prepare_run(config, profile_name, user_args, base_env=None, claude_settings_env=None):
    base_env = dict(os.environ if base_env is None else base_env)
    provider, profile = profile_for(config, profile_name)
    profile_env = profile.get("env", {})
    env = dict(base_env)
    expansion_env = dict(base_env)
    if provider == "claude":
        settings_env = load_claude_settings_env() if claude_settings_env is None else claude_settings_env
        expansion_env = {**settings_env, **base_env}

    if provider == "claude":
        argv = ["claude"]
        settings_env = {key: expand_value(value, expansion_env) for key, value in profile_env.items()}
        if settings_env:
            argv += ["--settings", json.dumps({"env": settings_env})]
        argv += user_args
    else:
        die(f"unsupported provider for {profile_name}: {provider}")

    return argv, env


def redact(data):
    redacted = copy.deepcopy(data)

    def walk(value, key=""):
        if isinstance(value, dict):
            for child_key, child_value in value.items():
                if SECRET_RE.search(child_key) and isinstance(child_value, str):
                    value[child_key] = "<redacted>"
                else:
                    walk(child_value, child_key)
        elif isinstance(value, list):
            for item in value:
                walk(item, key)

    walk(redacted)
    return redacted


def print_usage():
    print(
        """usage:
  aweswitch <profile> [agent args...]
  aweswitch list
  aweswitch show <profile>
  aweswitch config path
  aweswitch config show
  aweswitch config edit
  aweswitch config init
  aweswitch init"""
    )


def command_list(config):
    for provider in sorted(config["profiles"]):
        provider_profiles = config["profiles"][provider]
        if not isinstance(provider_profiles, dict):
            die(f"provider profiles must be an object: {provider}")
        for name in sorted(provider_profiles):
            profile = provider_profiles[name]
            model = profile_model_label(provider, profile)
            print(f"{name}\t{provider}\t{model}")


def profile_model_label(provider, profile):
    if provider == "claude":
        return profile.get("env", {}).get("ANTHROPIC_MODEL", "?")
    return "?"


def command_show(config, name):
    _, profile = profile_for(config, name)
    print(json.dumps(redact(profile), indent=2))


def editor_argv(editor, path):
    return [*shlex.split(editor), str(path)]


def exec_agent(argv, env):
    try:
        os.execvpe(argv[0], argv, env)
    except FileNotFoundError:
        die(f"command not found: {argv[0]}")
    except OSError as exc:
        die(f"failed to run {argv[0]}: {exc}")


def command_config(argv):
    path = config_path()
    subcommand = argv[0] if argv else "path"

    if subcommand == "path":
        print(path)
    elif subcommand == "show":
        print(json.dumps(redact(load_config(path)), indent=2))
    elif subcommand == "init":
        init_config(path)
        print(path)
    elif subcommand == "edit":
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            init_config(path)
        editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or shutil.which("nano")
        if not editor:
            die(f"no EDITOR set; edit config manually: {path}")
        argv = editor_argv(editor, path)
        os.execvp(argv[0], argv)
    else:
        die(f"unknown config command: {subcommand}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help", "help"):
        print_usage()
        return 0

    if argv[0] == "config":
        command_config(argv[1:])
        return 0
    if argv[0] == "init":
        init_config(config_path())
        print(config_path())
        return 0

    config = load_config(config_path())
    if argv[0] == "list":
        command_list(config)
        return 0
    if argv[0] == "show":
        if len(argv) != 2:
            die("usage: aweswitch show <profile>")
        command_show(config, argv[1])
        return 0

    run_argv, run_env = prepare_run(config, argv[0], argv[1:])
    exec_agent(run_argv, run_env)


if __name__ == "__main__":
    raise SystemExit(main())
