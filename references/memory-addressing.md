# 记忆寻址（memory-addressing）

写端四个子命令共用本文件；intake 读取宿主记忆库亦按其定位。**目标不是记住某个路径，而是每次现场确定"这个 agent 的记忆在哪、长什么样"。**

## 一、优先级（四层）：宿主自述 > 规则文件 > 通用探测 > 兜底

### 1. 宿主自述（最高优先）

宿主通常知道自己的记忆位，并可能直接告诉你。先检查**系统提示、上下文或工具说明**里有没有明确给出记忆目录（例：`Your memory directory is …`、`memoryRoot`、记忆工具的路径参数）。有 → `[ -d ]` 检存后直接用，本文件后面的层全部作废。

### 2. 规则文件

系统/上下文没给，就在当前工作区根目录按序找，读到哪个算哪个：

`AGENTS.md` → `CLAUDE.md` → `QODER.md` → `GEMINI.md` → `.cursor/rules/` → `.github/copilot-instructions.md`

在文件里搜"记忆 / memory / learnings"章节。只要它规定了目录或格式，**照它写**，本文件后面的层全部作废。

例：某仓库 `CLAUDE.md` 写了"重要决策通过 super-memory 归档、实时记录写 `.learnings/`、成熟规则写回本文件"——那就按这三条走，别再猜宿主。

### 3. 通用探测（不硬编码宿主名）

前两层都没有，用 glob 实测本机所有记忆位——**别按宿主名单逐个猜，让文件系统回答**：

```bash
# 打印实际存在的记忆位，探测结果要出现在给用户的输出里
shopt -s nullglob dotglob   # 必须！否则会漏掉所有点目录
for p in ~/*/memory ~/*/memories ~/*/projects/*/memory ~/*/cli/memories/projects/*/memory \
         ~/*/memory/projects/* ~/*/memories/*/global ~/*/memories/*/projects/*; do
  [ -d "$p" ] || continue
  # junction/符号链接会让同一实体出现多条路径——realpath 只留一份
  echo "DIR  $(realpath -m "$p" 2>/dev/null || echo "$p")"
done
for f in ./memory/MEMORY.md ~/AGENTS.md ~/QODER.md; do [ -e "$f" ] && echo "FILE $f"; done
```

**多命中时的裁决顺序**（逐条过，不许瞎猜）：

1. 宿主自述的路径最优先（有则回到第 1 层）
2. 只挑**属于当前宿主**的目录——你从系统提示/工具集知道自己跑在哪个宿主里（如 ZCode 带 `project_memory_*`/`memory_update` 系工具），别把 Qoder 的目录写进 ZCode 的会话
3. 项目级候选与当前工作区对号：按「已知形态」表的定位方式比对（slug 反查 / ZCode 型哈希精算 / 读候选 `MEMORY.md` 内容找路径线索）
4. 仍并列 → 比 `MEMORY.md` 的 mtime，取更新的
5. 无法分辨 → **列出候选 + 证据问用户**；写错位置比没写更糟

**已知形态**（校验参考，不是结论；2026-10 实测）：

| 宿主 | 用户级（跨项目） | 项目级（单项目） | 项目定位方式 |
|---|---|---|---|
| Qoder | `~/.qoder/memory/` | `~/.qoder/projects/<slug>/memory/` | slug=绝对路径把盘符冒号、`\`、`/`、空格**及所有非 ASCII（含中文）**换成 `-`；会话 jsonl 内 `"cwd"` 可反查 |
| QoderCN | `~/QODER.md` | `~/.qoder-cn/memories/<id>/{global,projects}/<slug>/` | slug 保留中文 |
| ZCode | （未见用户级） | `~/.zcode/cli/memories/projects/<名>-<hash16>/memory/` | **可精算**：`sha256(小写工作区根)[:16]`；目录名 = basename 小写、非 `[a-z0-9._-]` 变 `-`、截 48 的前缀 + `-` + hash |
| Trae CN | `~/.trae-cn/memory/{user_profile.md,…}` | `~/.trae-cn/memory/projects/<slug>/` | 以 `-` 开头、CJK→`-`；新版带 `-p2-<hex>` 后缀**不可算**，靠 `project_memory.md` 内容与 mtime 校验 |
| Codex CLI | `~/.codex/memories/` | 无目录级，条目内 `applies_to: cwd=…` 标项目 | 按内容字段匹配当前工作区 |
| WorkBuddy | `~/.workbuddy/`（`MEMORY.md`、`user-<uid>-personal/`） | 未见 | — |
| Claude Code | `~/.claude/memory/`（若存在） | `~/.claude/projects/<slug>/memory/` | 同 Qoder 风格（未实测） |
| 无托管记忆 | — | 项目根 `memory/` + `MEMORY.md` | 仓库/工作区根 |

ZCode 精算（先 `ls` 反查目录列表，命中即用；找不到再按规则新建）：

```bash
python -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].lower().encode()).hexdigest()[:16])" "<工作区绝对路径>"
ls ~/.zcode/cli/memories/projects/   # 反查：目录名前缀与工作区 basename 比对
```

**slug 类目录别手算，用现有目录对**：`ls <宿主>/projects/` 里找得到就用它，找不到再按规则新建。

### 4. 兜底

一个都没探测到 → 用项目根 `memory/` + `memory/MEMORY.md` 索引，并在变更摘要中写明"未找到宿主记忆位"。

## 二、两级分流：这条该进用户级还是项目级

只问一句：**换一个项目，这条还成立吗？**

| 类型 | 成立范围 | 去处 |
|---|---|---|
| 用户角色、技术背景、长期偏好 | 所有项目 | 用户级 |
| 协作习惯（怎么汇报、怎么确认、什么时候该停下来） | 所有项目 | 用户级 |
| 只在本项目成立的事实、决策、约束、进度 | 单项目 | 项目级 |
| 本项目专属的外部资源（看板、文档站、部署地址） | 单项目 | 项目级 |
| 某工具的通用用法、和具体项目无关 | 所有项目 | 用户级 |

判不准就**放项目级**——项目级写错了下次还能捞，用户级污染了会跟着所有项目。

## 三、格式：贴现存条目，不要自创

1. 列出目标目录的现有条目，读 1–2 个。
2. 照抄它的字段结构。多数 agent 记忆库形如：

```markdown
---
name: <与文件名一致的 kebab-case>
description: <一行，将来靠它判断相关性，写具体>
last_verified: <YYYY-MM-DD，可选；写了它 neat 才能提示超龄重验>
metadata:
  type: user | project | feedback | reference
---

<正文。事实本身 + Why + How to apply>
```

3. 更新索引（`MEMORY.md`），每个条目一行：

```markdown
- [标题](文件名.md) — 一行钩子
```

索引只放指针，不放正文。

## 四、和宿主自动记忆机制共存

宿主本身可能在写同一批目录。写前必做：

```bash
grep -rin "<本条关键字>" <目标目录>/MEMORY.md <目标目录>/*.md
```

- 命中 → 编辑已有条目（改内容 + 必要时改 description），**不新建**。
- 未命中 → 新建条目 + 追加索引行。
- 两边同时改过同一条 → 以磁盘当前内容为准做合并，别用记忆里的旧版覆盖。
