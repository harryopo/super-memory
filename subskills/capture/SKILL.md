# Capture — 实时捕获与记录

> `super-memory` 的 capture 子命令。检测到错误 / 纠正 / 学习 / 特征请求时按结构写入 `.learnings/`。
> 本文件由父级用 Read 加载，不是独立 skill；工具授权看父级 frontmatter。

## 写之前

`.learnings/` 是**暂存层**：装未升档的实时记录。已验证且跨模块通用的结论要升档到 `.ai/knowledge/`（见 handoff），归属划分见 `../../references/knowledge-tiers.md`。

`.learnings/` 相对于**当前工作区根目录**。跨项目工作时，改了哪个项目就写哪个项目的 `.learnings/`，别全堆在一个目录里；拿不准就问一句。

首次使用补齐目录与三个聚合文件，**已存在的绝不覆盖**：

```bash
mkdir -p .learnings
[ -f .learnings/LEARNINGS.md ] || printf '# Learnings\n\nCorrections, insights, and knowledge gaps captured during development.\n\n---\n' > .learnings/LEARNINGS.md
[ -f .learnings/ERRORS.md ] || printf '# Errors\n\nCommand failures and integration errors.\n\n---\n' > .learnings/ERRORS.md
[ -f .learnings/FEATURE_REQUESTS.md ] || printf '# Feature Requests\n\nCapabilities requested by the user.\n\n---\n' > .learnings/FEATURE_REQUESTS.md
```

**先查重再落盘**：`grep -rin "<本条关键字>" .learnings/`。命中已有条目 → 编辑那条（补 Status / See Also / Recurrence-Count），不新建第二条。同目录可能已有 self-improving-agent 写入的记录，这条规则同样适用于它。

## 快速参考

| 情况 | 写到哪 | 标识 |
|------|--------|------|
| 命令/操作失败、API 或工具报错 | `.learnings/ERRORS.md` | `ERR` |
| 用户纠正了做法 | `.learnings/LEARNINGS.md` | `LRN`，category `correction` |
| 知识过时、文档与实际不符 | `.learnings/LEARNINGS.md` | `LRN`，category `knowledge_gap` |
| 发现更好做法 | `.learnings/LEARNINGS.md` | `LRN`，category `best_practice` |
| 用户要一个不存在的能力 | `.learnings/FEATURE_REQUESTS.md` | `FEAT` |
| 与已有条目相关 | 就地加 `- See Also: <ID>` | — |
| 已验证且跨模块通用 | 升档 `.ai/knowledge/`（见 handoff），原条目留指针并标已升档 | — |
| 是必须每次看到的硬规则 | 转 promote 进规则文件 | — |

## ID 规则

`TYPE-YYYYMMDD-NNN`，NNN 是**当天同类型条目数 + 1**，用命令算，不许随机：

```bash
T=LRN; D=$(date +%Y%m%d)
case $T in LRN) F=.learnings/LEARNINGS.md;; ERR) F=.learnings/ERRORS.md;; FEAT) F=.learnings/FEATURE_REQUESTS.md;; esac
N=$(($(grep -c "^## \[$T-$D-" "$F" 2>/dev/null) + 1))
printf '%s-%s-%03d\n' "$T" "$D" "$N"
```

## 条目格式（唯一权威）

三条聚合文件里每个条目都以 `## [ID] <短标题>` 开头，字段各占一行，`**键**： 值` 形式。

```markdown
## [LRN-20260929-001] 部署必须走 env 里的目标路径

**Logged**: 2026-09-29
**Priority**: high
**Status**: pending
**Category**: correction
**Area**: infra

**Summary**：一句话讲清这条学习。

**Details**：发生了什么、原来错在哪、正确的是什么。

**Suggested Action**：具体到能直接照着做的动作。

**Metadata**
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- See Also: LRN-20260928-003
- Recurrence-Count: 1
- Tags: 部署 rsync deployment
```

`Tags` 规则：2–4 个检索词，**中文词 + 英文词 + 领域词各一**（换词也命中的关键——写入时多花 5 秒，检索时省三轮 grep）；领域词从 Area 取或自拟。

`ERRORS.md` 用同一骨架，把 `Category` 换成 `**Error**` 代码块（贴原始报错，脱敏后），并加 `- Reproducible: yes | no | unknown`。
`FEATURE_REQUESTS.md` 用同一骨架，正文字段为 `**Requested Capability**` / `**User Context**` / `**Complexity Estimate**` / `**Suggested Implementation**`，Metadata 加 `- Frequency: first_time | recurring`。

优先级：`critical` 阻塞核心功能或有数据丢失风险 · `high` 影响常用流程或反复出现 · `medium` 有变通方案 · `low` 边界情况。
Area 按项目实际取（`frontend` `backend` `infra` `tests` `docs` `config` 等），不是这几类就自己定一个，别硬套。

### 解决条目

```markdown
**Resolution**
- **Resolved**: 2026-09-30
- **Commit/PR**: abc123
- **Notes**: 做了什么
```

`**Status**` 取值：`pending` → `in_progress` → `resolved`；不处理记 `wont_fix` 并写明原因；被提炼成规则记 `promoted`（见 promote）。

## 历史遗留格式

真实仓库里常见另外两种形态：**日期叙事文件**（`2026-08-09-deep-check.md`，正文是任务流水）和**一条一文件**（`LRN-20260723-001-xxx.md`）。

- 新条目一律进三个聚合文件，按上面的格式。
- 历史文件**不重写、不迁移**（除非用户明确要求）。它们是既有记录，只在 neat 审查时按"事实现在还成立吗"来判断。
- 所有扫描命令必须同时认这三代形态，见下面的写法。

## 扫描命令（照抄可用）

键名可能带 `**` 也可能不带，类别可能在标题行也可能在字段行，所以一律用 `[*]*` 与"或"式匹配：

```bash
# 待处理条目数（三种形态全覆盖）
grep -rEc "Status\**:[[:space:]]*pending" .learnings/ 2>/dev/null | awk -F: '{s+=$NF} END{print "pending:", s+0}'

# 高优先级待处理
grep -rE "Priority\**:[[:space:]]*(high|critical)" .learnings/ || echo "无命中"

# 反复出现、够 promote 门槛（含 10 以上）
grep -rE "Recurrence-Count\**:[[:space:]]*([3-9]|[1-9][0-9])" .learnings/ || echo "无命中"

# 已解决但未提炼的候选
grep -rlE "Status\**:[[:space:]]*resolved" .learnings/ || echo "无命中"
```

**0 命中不是通过**：把"无命中"原样报给用户，并分辨是"确实没有这类条目"还是"路径或格式没对上"（后者要回头修格式，不是报通过）。

## 安全边界

- 不写密钥、token、私钥、环境变量值。读到的配置默认按"含密钥"处理——只列键名，值一律打码，且逐层打码（顶层键名干净不代表嵌套 env 里没有令牌）。
- 不粘贴完整转录、完整源码或完整配置文件，只写短摘要与脱敏摘录。
