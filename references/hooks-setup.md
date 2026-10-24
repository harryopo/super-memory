# hooks 自动触发（可选安装件）

super-memory 的写入端默认靠触发词（用户开口）或 agent 自觉。要解决两个被动缺口——**会话开始不读记忆**（冷启动）与**会话结束不主动归档**——可以在宿主的 hooks 里注入提醒。本文件给 Claude Code 形态的配置片段；ZCode / Qoder 等宿主各有等价机制，按各自文档映射这三个时机即可。**不装也能用，此文件不影响 skill 本体。**

## 四个时机

| 时机 | 注入内容 | 解决什么 |
|---|---|---|
| SessionStart | 调用 `hook_session_intro.py`：存在 `.ai/HANDOFF.md` 时**直接打印 §0 当前快照** | 记忆冷启动（零动作获得状态） |
| PostToolUse（Bash） | 调用 `hook_capture_reminder.py`：命令失败时提醒 capture | 该记的没记（单人场景最大损失） |
| PreCompact | 上下文压缩前提醒跑 capture + handoff 压缩保全（至少刷新 §0 快照 + §3 断点） | 压缩丢上下文前抢救关键信息 |
| SessionEnd / Stop | 提醒跑 capture → handoff → save 最小闭环 | 被动收尾 |

## Claude Code 配置片段（~/.claude/settings.json）

> 安装位按宿主而定；下面模板以 skill 装在 `~/.zcode/skills/super-memory/` 为例，其他安装位替换路径即可。

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.zcode/skills/super-memory/scripts/hook_session_intro.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.zcode/skills/super-memory/scripts/hook_capture_reminder.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[super-memory] 上下文即将压缩：先 capture（未记的错误/纠正）→ handoff 压缩保全（至少刷新 §0 快照与 §3 断点），再允许压缩。'"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[super-memory] 会话收尾检查：本轮有无未 capture 的错误/纠正？HANDOFF 与记忆库是否需要更新（capture → handoff → save）？'"
          }
        ]
      }
    ]
  }
}
```

## 注意

- 片段只注入**文字提醒**，不代替 skill 执行；agent 收到后按对应子命令流程走。
- 命令在项目根目录执行，`[ -f .ai/HANDOFF.md ]` 已做存在性判断，无交接文件的项目静默通过。
- 时机名以宿主当前文档为准（Claude Code hooks: https://docs.claude.com/en/docs/claude-code/hooks ）；Stop 在部分版本不可配时，可用 SessionEnd 或退化为只在 SessionStart/PreCompact 注入。
- 若同时使用 claude-mem 等自动记忆插件，**二者会双写**：super-memory 与插件各管各的目录时可以共存，但不要让插件把内容也写进 `.ai/` 或 `.learnings/`（super-memory 对这两处的格式与历史有排他权威）。
