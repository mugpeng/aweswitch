# aweswitch

`aweswitch` 是一个轻量启动器，用来快速切换 Claude Code 的运行时 profile。

它从 `~/.config/aweswitch/config.json` 读取配置，只在启动进程时注入环境变量，然后启动 Claude Code。它不会修改 Claude 原始配置文件。

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
```

额外参数会透传给底层 agent：

```bash
aweswitch cc-glm --dangerously-skip-permissions
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

## Profile 规则

- Profile 按 provider 分组，目前放在 `profiles.claude` 下。
- 所有 provider 分组下的 profile 名必须全局唯一。
- Claude profile 会通过运行时 `--settings '{"env": ...}'` 传入 `env`，和 Claude Code 原生 settings 机制一致；Claude 模型通过 `env.ANTHROPIC_MODEL` 配置。
- `env` 只作用于本次启动的子进程。
- `${VAR_NAME}` 会从当前 shell 环境变量中展开。
- Claude profile 在 shell 没有设置 `${ANTHROPIC_AUTH_TOKEN}` 这类 token 变量时，也可以从 `~/.claude/settings.json` 的 `env` 中展开。
- 暂时不支持 Codex 和 Hermes profile。

## Claude 模型覆盖

对于 Claude profile，`ANTHROPIC_MODEL` 是主模型配置。

`ANTHROPIC_DEFAULT_HAIKU_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、
`ANTHROPIC_DEFAULT_OPUS_MODEL` 默认都不配置。

如果你希望 Claude Code 对轻量任务或后台任务使用更轻的模型，可以手动在
`~/.config/aweswitch/config.json` 里增加 `ANTHROPIC_DEFAULT_HAIKU_MODEL`。
可以用下面的命令查看或编辑配置：

```bash
aweswitch config path
aweswitch config show
aweswitch config edit
```

示例：

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

这样主模型仍然使用 `mimo-v2.5-pro`，同时让 Claude Code 在轻量/后台功能上
可以使用 `mimo-v2.5`。

## 环境变量

运行 profile 前，需要配置该 profile 引用的 token 环境变量：

```bash
export ANTHROPIC_AUTH_TOKEN="..."
export GEMINI_ANTHROPIC_AUTH_TOKEN="..."
export XIAOMI_ANTHROPIC_AUTH_TOKEN="..."
```

如果希望每次打开终端都可用，可以把这些变量放进 `~/.zshrc`。

## 测试

运行：

```bash
python3 tests/test_aweswitch.py
```
