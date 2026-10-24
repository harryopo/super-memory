# 语义检索（opt-in 语义层）

> 核心 skill 的检索是 grep + Tags + `scripts/search.py`（BM25-lite）——**零依赖且已覆盖绝大多数场景**。
> 本文件是**可选的第三层**：给"忘了关键词、只记得意思"的真·语义召回。只有当记忆库达到千条级、
> 且换词三连+Tags+search.py 仍频繁漏召回时才值得启用。启用前把这条纪律读两遍：
> **embedding 索引是 sidecar（旁路缓存），Markdown 文件仍是唯一权威——索引丢了/旧了随时可重建。**

## 方案：fastembed + sqlite-vec（本机 CPU，无服务）

| 组件 | 选型 | 理由 |
|---|---|---|
| embedding | `fastembed`（ONNX，CPU） | 免 GPU、免服务、模型 ~100MB 首次下载后离线 |
| 向量存储 | `sqlite-vec`（sqlite 扩展） | 单文件 sidecar（如 `.ai/index.vec`），与 Markdown 同目录 |
| 切分 | 按条目（`## [ID]` 块 / frontmatter 文件） | 与记忆条目天然对齐 |

## 启用（一次性）

```bash
pip install fastembed sqlite-vec
```

## 索引重建（写后纪律）

记忆写入/修改后重建（全量重建在千条级 < 10 秒，增量优化等真需要再做）：

```bash
python scripts/semantic_index.py --root .   # 【未实现——本文件是方案文档，启用时再写】
```

重建触发点与 handoff 收尾同轮（neat 自检可加一条"索引新鲜度：mtime 晚于最旧 .md"）。

## 查询分工

| 场景 | 用什么 |
|---|---|
| 有关键词 | grep / Tags / `scripts/search.py`（快、准、可解释） |
| 只记得意思 | 语义查询（Top-K + 阈值），命中后**仍要回读 Markdown 原文** |
| 查重（四操作） | grep + Tags 优先，语义相似度做辅助信号（同人不同词的重复条目主要靠它） |

## 明确的代价

- 引入 pip 依赖与模型文件（~100MB）——破坏"零依赖"纯粹性，故做成 opt-in
- 索引是派生物：**只读不写**，过期就重建，绝不把向量库当事实源
- 不进 CI、不进核心门禁——它是增强，不是依赖
