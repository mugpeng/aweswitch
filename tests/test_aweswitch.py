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
            self.assertIn("claude", data["profiles"])
            self.assertIn("cc-glm", data["profiles"]["claude"])
            self.assertNotIn("codex", data["profiles"])

    def test_prepare_claude_uses_provider_command_and_env_overrides(self):
        config = {
            "profiles": {
                "claude": {
                    "cc-glm": {
                        "env": {
                            "ANTHROPIC_BASE_URL": "${GLM_BASE}",
                            "ANTHROPIC_AUTH_TOKEN": "${GLM_TOKEN}",
                            "ANTHROPIC_MODEL": "glm-5.1",
                        },
                    }
                }
            }
        }
        base_env = {"PATH": "/bin", "GLM_BASE": "https://example.test", "GLM_TOKEN": "secret"}

        argv, env = aweswitch.prepare_run(config, "cc-glm", ["--verbose"], base_env)

        self.assertEqual(argv, [
            "claude",
            "--settings",
            json.dumps({
                "env": {
                    "ANTHROPIC_BASE_URL": "https://example.test",
                    "ANTHROPIC_AUTH_TOKEN": "secret",
                    "ANTHROPIC_MODEL": "glm-5.1",
                }
            }),
            "--verbose",
        ])
        self.assertNotIn("ANTHROPIC_MODEL", env)
        self.assertNotIn("ANTHROPIC_BASE_URL", env)
        self.assertNotIn("ANTHROPIC_AUTH_TOKEN", env)
        self.assertEqual(base_env.get("ANTHROPIC_MODEL"), None)

    def test_prepare_claude_can_expand_from_claude_settings_env(self):
        config = {
            "profiles": {
                "claude": {
                    "cc-glm": {
                        "env": {
                            "ANTHROPIC_BASE_URL": "${ANTHROPIC_BASE_URL}",
                            "ANTHROPIC_AUTH_TOKEN": "${ANTHROPIC_AUTH_TOKEN}",
                            "ANTHROPIC_MODEL": "glm-5.1",
                        },
                    }
                }
            }
        }
        claude_settings_env = {
            "ANTHROPIC_BASE_URL": "https://example.test",
            "ANTHROPIC_AUTH_TOKEN": "secret",
        }

        argv, env = aweswitch.prepare_run(config, "cc-glm", [], {}, claude_settings_env)

        self.assertEqual(argv, [
            "claude",
            "--settings",
            json.dumps({
                "env": {
                    "ANTHROPIC_BASE_URL": "https://example.test",
                    "ANTHROPIC_AUTH_TOKEN": "secret",
                    "ANTHROPIC_MODEL": "glm-5.1",
                }
            }),
        ])
        self.assertEqual(env, {})

    def test_prepare_claude_only_uses_settings_env_for_model(self):
        config = {
            "profiles": {
                "claude": {
                    "cc-glm": {
                        "env": {
                            "ANTHROPIC_BASE_URL": "https://example.test",
                            "ANTHROPIC_AUTH_TOKEN": "secret",
                            "ANTHROPIC_MODEL": "glm-5.1",
                        },
                    }
                }
            }
        }
        base_env = {"ANTHROPIC_MODEL": "old-model"}

        argv, env = aweswitch.prepare_run(config, "cc-glm", [], base_env)

        self.assertEqual(env["ANTHROPIC_MODEL"], "old-model")
        self.assertEqual(argv, [
            "claude",
            "--settings",
            json.dumps({
                "env": {
                    "ANTHROPIC_BASE_URL": "https://example.test",
                    "ANTHROPIC_AUTH_TOKEN": "secret",
                    "ANTHROPIC_MODEL": "glm-5.1",
                }
            }),
        ])

    def test_prepare_claude_ignores_top_level_model(self):
        config = {
            "profiles": {
                "claude": {
                    "cc-glm": {
                        "model": "ignored-model",
                        "env": {
                            "ANTHROPIC_BASE_URL": "https://example.test",
                            "ANTHROPIC_AUTH_TOKEN": "secret",
                            "ANTHROPIC_MODEL": "glm-5.1",
                        },
                    }
                }
            }
        }

        argv, env = aweswitch.prepare_run(config, "cc-glm", [], {})

        self.assertEqual(env, {})
        self.assertNotIn("--model", argv)
        self.assertNotIn("ignored-model", argv)

    def test_prepare_rejects_codex_profiles_for_now(self):
        config = {
            "profiles": {
                "codex": {
                    "codex-mini": {
                        "model": "gpt-5.4-mini",
                        "env": {"OPENAI_API_KEY": "${OPENAI_API_KEY}"},
                    }
                }
            }
        }

        with self.assertRaisesRegex(SystemExit, "unsupported provider"):
            aweswitch.prepare_run(config, "codex-mini", ["--help"], {})

    def test_profile_model_label_uses_anthropic_model_for_claude(self):
        self.assertEqual(
            aweswitch.profile_model_label("claude", {"env": {"ANTHROPIC_MODEL": "glm-5.1"}}),
            "glm-5.1",
        )

    def test_profile_for_errors_on_duplicate_profile_names(self):
        config = {
            "profiles": {
                "claude": {"default": {"env": {}}},
                "codex": {"default": {"env": {}}},
            }
        }

        with self.assertRaisesRegex(SystemExit, "ambiguous profile"):
            aweswitch.profile_for(config, "default")

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
