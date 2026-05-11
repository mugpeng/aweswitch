# aweswitch

`aweswitch` 是一个轻量启动器，用来快速切换 Claude Code 和 Codex 的运行时 profile。

它从 `~/.config/aweswitch/config.json` 读取配置，只在启动进程时注入环境变量或运行参数，然后启动对应 agent。它不会修改 Claude 或 Codex 原始配置文件。

## 安装

把脚本复制到 `PATH` 中的目录：

```bash
cp aweswitch.py ~/.local/bin/aweswitch
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

## Profile 规则

- `provider: "claude"` 启动 `claude`。
- `provider: "codex"` 启动 `codex`。
- Claude 的 `model` 会在运行时设置为 `ANTHROPIC_MODEL`，除非 profile 里显式写了 `env.ANTHROPIC_MODEL`。
- Codex 的 `model` 会作为 `--model <model>` 参数传入。
- `env` 只作用于本次启动的子进程。
- `${VAR_NAME}` 会从当前 shell 环境变量中展开。
- Claude profile 在 shell 没有设置 `${ANTHROPIC_*}` 时，也可以从 `~/.claude/settings.json` 的 `env` 中展开。

## 环境变量

如果自定义 provider，需要设置 profile 中引用的变量：

```bash
export ANTHROPIC_BASE_URL="..."
export ANTHROPIC_AUTH_TOKEN="..."
```

如果希望每次打开终端都可用，可以把这些变量放进 `~/.zshrc`。

## 测试

运行：

```bash
python3 tests/test_aweswitch.py
```
