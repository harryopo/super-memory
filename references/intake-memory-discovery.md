# 记忆文档探测（intake 用）

接手时**不假设**记忆文件在 `.ai/HANDOFF.md`——命名与位置千变万化（本机 40 项目实测）。先探、再按角色分类、再读。

## 一、探测清单（按实测命中率排序）

**Tier 1 — 容器目录**（先 `ls` 这些，存在即列）：

`.ai/`（含其子目录 `context/`、`knowledge/`、`tasks/`） · `.learnings/`（实测 14+ 项目命中，比 `.ai/` 更高频） · `memory/` · `.memory/` · `.workbuddy/memory/` · `.claude/memory/` · `.codex-memory/` · `docs/handoff/` 与 `docs/handoffs/` · `docs/wiki/` 与 `docs/repowiki/`

**Tier 1 — 文件名**（不分大小写，扫工作区 maxdepth 4）：

`HANDOFF*` `HANDOVER*` `*交接*` `*记忆*` `MEMORY.md` `LEARNINGS.md` `ERRORS.md` `FEATURE_REQUESTS.md` `PROGRESS*` `TASKS.md` `VERIFICATION.md` `PROJECT_BRIEF.md` `AGENTS.md` `CLAUDE.md`

**Tier 2 — 常用但项目特化**：

`ARCHITECTURE.md` `DECISIONS.md` `MAP.md` `SECURITY.md` `INDEX.md` `known_issues.md` `coding_standards.md` `dev-state*`（可能是 1MB 级进度真源，只看增量） `current-state.md` `project-map.md` `handoff-notes.md` `*现状*` `*规划*` `00-目标与进度.md` `踩坑记录.md` `项目进度*` `SESSION_*.md` kiro 风格 `project_*.md`/`user_profile.md`/`feedback_*.md`

**Tier 3 — 日期/编号变体**（用正则，别漏）：

`*-YYYYMMDD.md`（交接文档-20260911） · `*-YYYY-MM-DD.md`（交接总账-2026-09-25） · `*_YYYY-MM-DD_主题.md`（SESSION_2026-06-22_…） · `YYYY-MM-DD.md`（纯日期日记） · `vYYYY-MM-DD` / `*_V2.md`

**活跃度与新鲜度探测（mtime 是未提交工作的真值）**：

```bash
# 活跃开发区：最近 7 天改动的源码与文档（未提交的开发只在这里显形）
find . -maxdepth 3 -type f -newermt "-7 days" \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.md" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/.mimosa/*" 2>/dev/null | head -20
# 单目录热点：按修改时间排
ls -lt <关键模块目录>/ | head
```

**新鲜度三角**：记忆自述"最后更新" ↔ git HEAD 日期 ↔ 源码/记忆文件实际 mtime。三者对不齐＝记忆漂移（实战：HANDOFF 头部停在 09-30、末尾实际到 10-09、源码 mtime 同步到 10-09——只读头部就会得出"无未闭环工作"的错误结论）。同角色多份记忆文档，**mtime 最新的为权威**，旧的转历史参考。

**排除清单**（防误报，实战踩过）：

- `src/`、`tests/`、**`src-tauri/` 等源码树**下的同名文件（`handoff_manager.py`、`profile-handoff.ts` 是代码不是记忆）——最稳的办法是给 find 加 `-name "*.md"`：记忆文档必然是 .md，代码与 htmlcov 产物一次排除
- 工具状态目录：`.trae/specs/`（每特性一个 tasks.md，是规格不是进度）、`htmlcov/`、`node_modules/`、`.git/`、`dist/`、`build/`、`venv/`
- 第三方/参考目录整棵（一个 opensource-reference 含 150+ 个 AGENTS.md；也可能就在项目根内）
- 主题页误报：`docs/repowiki/*记忆*` 这类是"讲记忆系统的 wiki 页"，不是记忆本体——靠第二步角色嗅探排除，不靠文件名

参考命令（2026-10-10 实战修订版）：

```bash
# Tier1 容器快速探测
for d in .ai .learnings memory .memory .codex-memory docs/handoff docs/handoffs docs/wiki docs/repowiki; do
  [ -d "$d" ] && echo "DIR  $d"
done
# 文件名探测（限 .md；排除源码树/工具态/第三方）
find . -maxdepth 4 -name "*.md" \( -iname "*handoff*" -o -iname "*handover*" -o -iname "*交接*" -o -iname "*记忆*" \
  -o -iname "MEMORY.md" -o -iname "PROGRESS*" -o -iname "TASKS.md" -o -iname "dev-state*" \
  -o -iname "*现状*" -o -iname "*规划*" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/src/*" -not -path "*/src-tauri/*" \
  -not -path "*/tests/*" -not -path "*/opensource-reference/*" -not -path "*/.trae/*" 2>/dev/null
```

## 二、角色分类（不看文件名死认，读首 30 行判）

| 角色 | 判定线索（文件名 ∥ 内容特征） | 读取优先级 |
|---|---|---|
| 交接 | HANDOFF/HANDOVER/交接* ∥ 有进度、断点、下一步、交接口吻 | 1 |
| 进度 | PROGRESS/进度*/dev-state ∥ 时间线、完成度、日常站会式记录 | 2 |
| 概览 | PROJECT_BRIEF/README/项目记忆 ∥ 一页纸定位与总览 | 3 |
| 架构 | ARCHITECTURE/MAP ∥ 分层图、模块说明、目录地图 | 4 |
| 决策 | DECISIONS ∥ 编号决策、备选对比、权衡 | 5 |
| 任务 | TASKS/TODO/项目进度表 ∥ 勾选框、优先级、看板 | 6 |
| 规范 | coding_standards/context/*/AGENTS.md/CLAUDE.md ∥ 规则与禁令 | 7 |
| 踩坑 | known_issues/LEARNINGS/踩坑记录 ∥ 问题-根因-解法 | 8 |

**形态二分（决定从哪头读）**：**快照式**（覆盖重写，`最后核验` 在头部）从头读；**追加式**（按会话/编号追加，如 `## 52 · 2026-10-08`）**最新状态在文件末尾**——判"当前"先 `tail`、节清单全文枚举（`grep -cE "^## "` 后全列，**不许 head 截断**），头部 §1 可能是十几天前的开场快照。实战教训：213KB 追加式 HANDOFF 读头部得出"无未闭环工作项"，实际末尾 §52–§54 是发布后 33 个提交的活跃开发（2026-10-10 dogfood 实录）。

一个文件可能同时是"进度+交接"（多数中文交接文档如此）→ 按最高优先角色读一次即可，别重复读。

**平行标记体系**（实战常见）：项目可能自用 ✅⚠️❓📌 等符号而非 [V][W][Q][R][F]（例：HANDOFF 用 ✅=已验证、⚠️=进行中/有风险、❓=待确认、📌=已固化）。读取时**按语义映射**到字母码（✅→[V]、⚠️→[W] 或 [R]、❓→[Q]、📌→[F]），简报里注明映射关系；不要因符号不同判记忆无效。

## 全面分析三层次（intake A2 的操作细节）

"抽查式读"是进度误判的头号来源，读记忆必须走满三层：

1. **结构级**：节/日期清单**全文枚举**（`grep -E "^#+ " <文件>` 全列，禁止 head 截断），建时间轴——读完必须能复述"这份文件覆盖哪天到哪天、哪些会话"，答不出就是读得不全。
2. **内容级**：最新节全文读，其余节扫标题+日期；**"当前没有未闭环工作"类的声明必须出自当前状态源**——有 §0 快照的文件以 §0 为准（并核对最末节是否已同步进 §0），无 §0 的旧式文件以**最末节**为准，头部/中部小节的此类声明是过期快照。实战案例：213KB 追加式 HANDOFF 头部 §2.3 停在 09-30"无未闭环工作"，末尾 §52–§54 是 v0.9.2 发布后 33 个提交的活跃开发，只读头部即得出错误结论（2026-10-10 dogfood 实录，被用户当场纠正）。
3. **多源交叉**：同角色多份文档**全部要读**（HANDOFF + dev-state + 按日记忆……），互证取最新；只读一份就下结论＝没做全面分析。交叉时顺带比对各文件 mtime 与其自述"最后更新"是否一致。

## 检索纪律（找记忆时的搜索动作）

单轮 grep 不够，三层动作：

1. **换词三连**：中/英/同义词各搜一轮（错误↔踩坑↔failure、交接↔进度↔handoff、决策↔拍板↔decision）。
2. **补搜维度**：`Tags:` 字段、文件路径片段、日期（YYYYMMDD）、ID 前缀（LRN-/K-/ERR-）。
3. **排序检索**：多词查询用 `python <skill目录>/scripts/search.py "查询词" --root <工作区>`——BM25-lite（标题行 ×3 加权、CJK 二元组切词、自动排除 node_modules/.git/src 等噪声），输出 Top-N 文件与命中行。

三轮全空才可判"无"，并注明搜过哪些词——这本身就是给下个会话的记忆。

## 三、整理两模式（仅当散落/重叠时启用）

触发判据：同一职能 ≥2 份（如 `.ai/HANDOFF.md` 与 `docs/交接文档.md` 并存）、跨容器散落（一部分 `.ai/` 一部分 `docs/`）、或命名混乱到无法判断新旧。

**模式 1：索引归位（默认，零风险）**——不动任何原文件，立/刷新一个入口索引（`.ai/HANDOFF.md` §6 或项目既有索引文件），逐条给：角色 → 路径 → 置信度 → 是否最新。唯一动作是写索引。

**模式 2：物理归并（须用户确认）**——产出整理方案表（# / 文件 / 现状 / 建议动作 / 目标位置），用户确认后执行：

- 纯移动：`mv` 到标准位置，登记新旧路径；随后 grep 全库清理指向旧路径的引用
- 内容合并：合并进目标文件；被合并掉的源文件 `mv` 进 `.tmp/neat-quarantine/<日期>/`（不 `rm`）
- 确认门与执行规范完全复用 `../../references/delete-review-template.md`（四选项 + 隔离 + 摘要登记）

**禁止**：未经确认移动/合并任何记忆文档；把第三方目录里的 AGENTS.md 当本项目记忆处理。
