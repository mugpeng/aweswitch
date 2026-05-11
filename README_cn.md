# aweswitch

`aweswitch` 是一个轻量启动器，用来快速切换 Claude Code 和 Codex 的运行时 profile。

它从 `~/.config/aweswitch/config.json` 读取配置，只在启动进程时注入环境变量或运行参数，然后启动对应 agent。它不会修改 Claude 或 Codex 原始配置文件。

## 安装

把脚本复制到 `PATH` 中的目录：

```bash
cp aweswitch.py ~/.local/bin/aweswitch
cp default-config.json ~/.local/bin/default-config.json
chmod +x ~/.local/bin/aweswitch
```

确认 `~/.local/bin` 已经在 `PATH` 里：

```bash
echo $PATH
```

如果没有，把下面这行加入 `~/.zshrc`：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

然后重新加载 shell：

```bash
source ~/.zshrc
```

## 快速开始

创建默认配置：

```bash
aweswitch config init
```

查看 profile 列表：

```bash
aweswitch list
```

查看某个 profile：

```bash
aweswitch show cc-glm
```

启动 profile：

```bash
aweswitch cc-glm
aweswitch codex-mini
```

额外参数会透传给底层 agent：

```bash
aweswitch cc-glm --dangerously-skip-permissions
aweswitch codex-mini --cd /path/to/project
```

## 配置文件

默认配置路径：

```bash
~/.config/aweswitch/config.json
```

常用配置命令：

```bash
aweswitch config path
aweswitch config show
aweswitch config edit
```

示例配置：

```json
{
  "profiles": {
    "cc-glm": {
      "provider": "claude",
      "env": {
        "ANTHROPIC_BASE_URL": "https://glm-provider.example.com/api/anthropic",
        "ANTHROPIC_AUTH_TOKEN": "${ANTHROPIC_AUTH_TOKEN}",
        "ANTHROPIC_MODEL": "glm-5.1"
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

## Profile 规则

- `provider: "claude"` 启动 `claude`。
- `provider: "codex"` 启动 `codex`。
- Claude profile 会通过运行时 `--settings '{"env": ...}'` 传入 `env`，和 Claude Code 原生 settings 机制一致；Claude 模型通过 `env.ANTHROPIC_MODEL` 配置。
- Codex 的 `model` 会作为 `--model <model>` 参数传入。
- `env` 只作用于本次启动的子进程。
- `${VAR_NAME}` 会从当前 shell 环境变量中展开。
- Claude profile 在 shell 没有设置 `${ANTHROPIC_AUTH_TOKEN}` 这类 token 变量时，也可以从 `~/.claude/settings.json` 的 `env` 中展开。

## 环境变量

运行 profile 前，需要配置该 profile 引用的 token 环境变量：

```bash
export ANTHROPIC_AUTH_TOKEN="..."
export GEMINI_ANTHROPIC_AUTH_TOKEN="..."
export XIAOMI_ANTHROPIC_AUTH_TOKEN="..."
export OPENAI_API_KEY="..."
```

如果希望每次打开终端都可用，可以把这些变量放进 `~/.zshrc`。

## 测试

运行：

```bash
python3 tests/test_aweswitch.py
```
