# 新项目初始化骨架（intake 场景 B 用）

**原则：按需裁剪，不预铺空文件。** 必备 3 件先建；可选项按项目规模选建；每个文件 = 标题 + 一行用途 + 占位符，**不写空节全文**。

## 一、必备 3 件

| 文件 | 内容 |
|---|---|
| `.ai/HANDOFF.md` | 按 `handoff-template.md` 十节写首版；无内容节留占位（`- （待填）`），★ 必需节不许省标题 |
| `.ai/knowledge/README.md` | 长期库索引：五分类用途表（decisions/patterns/problem-solutions/business/standards），注明"首条内容出现时才建对应分类目录" |
| `docs/wiki/index.md` | wiki 首页：导航骨架 + 维护四规则（见下） |

## 二、可选项（按项目规模选建）

| 文件 | 何时建 |
|---|---|
| `.ai/PROJECT_BRIEF.md` | 项目定位/受众需要被反复引用时（一页纸：是什么/给谁/边界） |
| `.ai/ARCHITECTURE.md` | 有多模块/多服务，或缺了它无法解释数据流时 |
| `.ai/TASKS.md` | 任务多于"下一步行动"一节能装下时 |
| `.ai/VERIFICATION.md` | 验证命令成套（lint/test/build/部署）时 |
| `.ai/context/coding_standards.md` | 有非默认编码约定时 |
| `.ai/context/known_issues.md` | 踩坑开始积累时 |
| `.ai/MAP.md` | 目录复杂到需要地图时（只给符号名优先于行号） |
| `docs/wiki/{domains,modules,api}/` | 有内容时才建对应子目录，首页先行 |

**不建**：空分类目录（`.ai/knowledge/` 的五个分类、wiki 子目录）、`.learnings/`（交给 capture 首次写入时自建）、`.ai/tasks/`、`.ai/releases/` 类工作目录（项目跑起来自然产生）。

## 三、各文件最小模板

```markdown
# PROJECT_BRIEF · <项目名>

> 最后核验：YYYY-MM-DD

## 是什么
<一句话业务定位>（待填）

## 给谁用
<目标用户与场景>（待填）

## 边界
- 做：<…>（待填）
- 不做：<…>（待填）
```

```markdown
# ARCHITECTURE · <项目名>

> 最后核验：YYYY-MM-DD

## 分层与数据流
<…>（待填）

## 模块职责
| 模块 | 路径 | 职责 |（待填）
```

其余（TASKS/VERIFICATION/coding_standards/known_issues/MAP）同理：标题 + `> 最后核验` 行 + 两三个空表的表头。**别预写内容**。

## 四、`docs/wiki/` 骨架

```markdown
# <项目名> Wiki

> 维护四规则：① 代码即真理——wiki 是代码的注释，代码变更后同步更新；② 分层索引——首页→领域→模块→文件；
> ③ 交叉引用——相关概念与模块用链接互指；④ 时效标记——每条记录标"最后验证"日期，过期即降级待核验。

## 导航
- [领域总览](domains/)（有内容后补链接）
- [模块说明](modules/)
- [接口文档](api/)
```

命名蓝本（本机实证：虚拟人智能体开发项目 `docs/wiki/`）：`index.md` 首页 + `01-架构总览.md`/`02-决策记录.md`/`03-部署指南.md` 等编号页；规模大时再拆 `domains/`、`modules/`、`api/` 子目录（FDE 项目实证）。项目已有 wiki 时保持其命名，别重排。

## 五、完成后

1. 运行 `python scripts/verify.py`（若 skill 所在仓可用）或手工核对目录清单
2. 向用户输出：建了什么（逐文件）/ 跳过了什么（理由）/ 下一步接线——开发结束 → handoff；错误纠正 → capture；阶段整理 → neat
3. 首个真实会话结束前不要往骨架里填"计划内容"——骨架等真实记忆，不做臆测填充
