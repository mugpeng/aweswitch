import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import aweswitch


class AweSwitchTests(unittest.TestCase):
    def test_init_creates_example_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"

            aweswitch.init_config(path)

            data = json.loads(path.read_text())
            self.assertIn("profiles", data)
            self.assertIn("cc-glm", data["profiles"])

    def test_prepare_claude_uses_provider_command_and_env_overrides(self):
        config = {
            "profiles": {
                "cc-glm": {
                    "provider": "claude",
                    "model": "glm-5.1",
                    "env": {
                        "ANTHROPIC_BASE_URL": "${GLM_BASE}",
                        "ANTHROPIC_AUTH_TOKEN": "${GLM_TOKEN}",
                    },
                }
            }
        }
        base_env = {"PATH": "/bin", "GLM_BASE": "https://example.test", "GLM_TOKEN": "secret"}

        argv, env = aweswitch.prepare_run(config, "cc-glm", ["--verbose"], base_env)

        self.assertEqual(argv, ["claude", "--verbose"])
        self.assertEqual(env["ANTHROPIC_MODEL"], "glm-5.1")
        self.assertEqual(env["ANTHROPIC_BASE_URL"], "https://example.test")
        self.assertEqual(env["ANTHROPIC_AUTH_TOKEN"], "secret")
        self.assertEqual(base_env.get("ANTHROPIC_MODEL"), None)

    def test_prepare_claude_model_overrides_existing_environment(self):
        config = {
            "profiles": {
                "cc-glm": {
                    "provider": "claude",
                    "model": "glm-5.1",
                }
            }
        }
        base_env = {"ANTHROPIC_MODEL": "old-model"}

        _, env = aweswitch.prepare_run(config, "cc-glm", [], base_env)

        self.assertEqual(env["ANTHROPIC_MODEL"], "glm-5.1")

    def test_prepare_codex_uses_model_flag_without_config_args(self):
        config = {
            "profiles": {
                "codex-mini": {
                    "provider": "codex",
                    "model": "gpt-5.4-mini",
                    "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"},
                }
            }
        }
        base_env = {"OPENAI_API_KEY": "secret"}

        argv, env = aweswitch.prepare_run(config, "codex-mini", ["--help"], base_env)

        self.assertEqual(argv, ["codex", "--model", "gpt-5.4-mini", "--help"])
        self.assertEqual(env["OPENAI_API_KEY"], "secret")

    def test_redact_hides_secret_values(self):
        data = {
            "profiles": {
                "x": {
                    "env": {
                        "ANTHROPIC_AUTH_TOKEN": "secret",
                        "ANTHROPIC_BASE_URL": "https://example.test",
                    }
                }
            }
        }

        redacted = aweswitch.redact(data)

        self.assertEqual(redacted["profiles"]["x"]["env"]["ANTHROPIC_AUTH_TOKEN"], "<redacted>")
        self.assertEqual(redacted["profiles"]["x"]["env"]["ANTHROPIC_BASE_URL"], "https://example.test")

    def test_expand_env_errors_on_missing_variable(self):
        with self.assertRaisesRegex(SystemExit, "missing environment variable"):
            aweswitch.expand_value("${MISSING_ENV}", {})

    def test_editor_argv_splits_editor_with_flags(self):
        argv = aweswitch.editor_argv("code -w", Path("/tmp/config.json"))

        self.assertEqual(argv, ["code", "-w", "/tmp/config.json"])

    def test_exec_agent_reports_missing_command(self):
        with self.assertRaisesRegex(SystemExit, "command not found"):
            aweswitch.exec_agent(["/tmp/aweswitch-command-that-does-not-exist"], {})


if __name__ == "__main__":
    unittest.main()
