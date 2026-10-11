# Promote — 学习提炼为规则

> `super-memory` 的 promote 子命令。把 `.learnings/` 里反复验证的学习提炼成短规则，写进项目的规则文件。
> 本文件由父级用 Read 加载，不是独立 skill；工具授权看父级 frontmatter。

## 什么时候推广

满足任一：

- `Recurrence-Count` ≥ 3，或同一问题跨 2 个以上不同任务出现
- 用户明确说"记住这个""以后都要这样"
- 属于任何贡献者（人或 AI）都该知道的项目事实或约定
- 能防止重复踩坑的边界规则、禁止事项、命令速查
- 条目已 `Status: resolved` 且有可复用的修复

**不推广的**：通用知识（"JS 用 const 不用 var"）、一次性事故复盘、详细机制说明（该进 `docs/`）、需要长篇背景才成立的内容。

## 流程

### 1. 扫候选

命令照抄，键名可能带 `**` 也可能不带，类别可能在标题行也可能在字段行：

```bash
grep -rE "Recurrence-Count\**:[[:space:]]*([3-9]|[1-9][0-9])" .learnings/ || echo "无命中"
grep -rlE "Status\**:[[:space:]]*resolved" .learnings/ || echo "无命中"
grep -rE "^## \[[A-Z]+-[0-9]{8}-[0-9]+\].*(best_practice|correction)" .learnings/ || echo "无命中"
```

`Category` 写在字段行时补一条：`grep -rE "Category\**:[[:space:]]*(best_practice|correction)" .learnings/`。

**0 命中必须报"无命中"**，并分辨是"确实没有候选"还是"条目格式没对上"——后者回去修 capture 的落盘格式，不要假装本轮推广完成。

### 2. 逐条过决策清单

- [ ] 跨 2 个以上文件/特性适用？
- [ ] 任何贡献者都该知道？
- [ ] 能防止重复犯错？
- [ ] 是本项目特定约定（不是通用知识）？
- [ ] 已验证可行（resolved 或有明确修复）？
- [ ] 提炼后 ≤ 2 句？
- [ ] 不是历史叙事？

多为"是" → 推广。多为"否" → 留在 `.learnings/` 继续观察。

### 3. 提炼

判据只有一条：**下次 AI 写代码时如果没看到这条，会不会犯错。** 会 → 值得进规则文件；只是"上次发生了什么" → 不值。

删掉所有时间叙事、情绪、调查过程，只留动作。

```
原始（verbose）：项目用 pnpm workspaces。试着跑 npm install 失败。锁文件是 pnpm-lock.yaml。必须用 pnpm install。
提炼（concise）：
## Build & Dependencies
- Package manager: pnpm (not npm) — use `pnpm install`
```

### 4. 选目标文件

先看项目里实际存在哪些规则文件（`ls AGENTS.md CLAUDE.md .github/copilot-instructions.md 2>/dev/null`），有哪个写哪个，别默认 `CLAUDE.md` 存在。

| 内容类型 | 写到哪 |
|---|---|
| 硬边界、禁止事项、命令速查、权限模型、协作流程 | 项目根规则文件（`AGENTS.md` / `CLAUDE.md`） |
| 跨模块通用的解法、技术决策、代码模式、业务规则 | `.ai/knowledge/` 对应分类（格式见 `../../references/knowledge-tiers.md`） |
| 工作流与自动化规则、多 agent 协作流程 | 规则文件；宿主另有约定文件时从约定 |
| 行为准则、沟通风格 | 宿主的人设/风格文件（若有） |

**先判归属再动手**：一条"上次这个 API 超时是因为连接池没设上限，设 20 解决"属长期库（`.ai/knowledge/problem-solutions/`），不是规则文件；"部署必须用完整 target 路径"才属规则文件。五处落点的完整判据见 `../../references/knowledge-tiers.md`。

只改当前项目的规则文件。跨项目通用的原则要不要进全局配置，须用户明确要求，不自己拍。

### 5. 写入

1. 读目标文件全文，找对应章节，没有就新建。
2. **插入前先 grep 同关键字**，已有等价规则 → 改那条，不叠第二条。
2b. 目标是 `.ai/knowledge/` 时：先按**巩固四操作**判定（ADD/UPDATE/SUPERSEDE/NOOP，见 `../../references/knowledge-tiers.md`），并检索相关旧条目双向 `**Related**` 互链、带 `**生效**`/`**记录**` 双时间戳。
3. 一条规则 ≤ 2 句，bullet 形式。
4. 规则里提到的路径、命令、工具，必须在代码里真实存在——写之前 `ls` 或 `grep` 确认一次。

### 6. 回写原条目

```markdown
**Status**: promoted

**Resolution**
- **Resolved**: 2026-09-30
- **Promoted**: CLAUDE.md §Build & Dependencies
- **Rule**: "Package manager: pnpm (not npm) — use `pnpm install`"
```

字段名与 capture 的骨架一致（`**Status**` / `**Resolution**`），别再引入第二套。

### 7. 验证

- 回读目标文件，确认规则在、位置对、没和现有规则打架
- 确认原条目 `Status` 已变 `promoted`
- `grep -E "今天|昨天|刚刚|最近|上周|today|yesterday|recently" <目标文件>` 清零

## 其他来源

| 来源 | 触发 | 去处 |
|---|---|---|
| neat 精简时发现精华 | 该条属规则而非叙事 | 直接进规则文件 |
| save 归档的跨项目适用偏好 | 用户明确认可 | 按 `../../references/memory-addressing.md` 分流到用户级记忆 |
| 用户说"把这个做成 skill" | 明确要求 | 交给 skill 开发工作台（`skill-workspace`），不在本命令里生成 |
