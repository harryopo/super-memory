#!/usr/bin/env python3
"""memory search — super-memory 的排序检索工具（零依赖，纯标准库）。

对记忆/文档 markdown 做词频加权检索（BM25-lite），中文按字符二元组切词。
比多轮 grep 高效：一次查询返回 Top-N 文件与最佳命中行。

用法:
  python scripts/search.py "查询词 查询词2" [--root 目录] [--top N] [--glob 模式]
  python scripts/search.py --selftest

设计约束：纯标准库、无网络、只读。排除噪声目录（node_modules/.git/dist/.mimosa 等）。
"""
import argparse
import math
import re
import sys
from pathlib import Path

NOISE = ("/node_modules/", "/.git/", "/dist/", "/build/", "/.mimosa/",
         "/.venv/", "/venv/", "/opensource-reference/", "/.trae/", "/htmlcov/")
DEFAULT_GLOB = "*.md"
CJK = re.compile(r"[\u4e00-\u9fff]")


def terms(text: str):
    r"""中英混合切词：拉丁词按 \w 切，CJK 按单字+二元组。"""
    out = []
    for w in re.findall(r"[a-zA-Z0-9_]+", text.lower()):
        if len(w) > 1:
            out.append(w)
    runs = re.findall(r"[\u4e00-\u9fff]+", text)
    for run in runs:
        out.extend(run[i:i + 2] for i in range(len(run) - 1))  # 二元组
        if len(run) == 1:
            out.append(run)
    return out


def iter_files(root: Path, pattern: str):
    for p in root.rglob(pattern):
        s = p.as_posix()
        if any(n in "/" + s for n in NOISE):
            continue
        if p.is_file():
            yield p


def score_file(path: Path, q_terms, avg_len: float, k1=1.5, b=0.75):
    """BM25-lite：标题行（#开头）词频 ×3 加权；返回 (得分, [命中行])。"""
    try:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0.0, []
    lines = raw.splitlines()
    tf = {}
    total = 0
    hits = []
    for i, line in enumerate(lines, 1):
        w = 3.0 if line.lstrip().startswith("#") else 1.0  # 标题加权
        lt = terms(line)
        total += len(lt)
        for t in set(q_terms):
            c = lt.count(t)
            if c:
                tf[t] = tf.get(t, 0) + c * w
                if len(hits) < 3 and t in terms(line):
                    hits.append((i, line.strip()[:110]))
    if not q_terms or total == 0:
        return 0.0, []
    score = 0.0
    for t in q_terms:
        f = tf.get(t, 0)
        if not f:
            continue
        idf = math.log(1 + 1.0)  # 单查询集内简化 IDF；多词时区分度靠词频
        score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * total / max(avg_len, 1)))
    return score, hits


def main(argv=None):
    ap = argparse.ArgumentParser(description="super-memory 排序检索（BM25-lite）")
    ap.add_argument("query", nargs="*", help="查询词（可多个）")
    ap.add_argument("--root", default=".", help="检索根目录")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--glob", default=DEFAULT_GLOB)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        base = Path(__file__).parent / "_selftest_corpus"
        c1 = base / "a-记忆.md"
        c2 = base / "b-other.md"
        c1.parent.mkdir(exist_ok=True)
        c1.write_text("# 部署踩坑\n\nrsync target 必须完整路径，上周因此部署失败。\n", encoding="utf-8")
        c2.write_text("# Unrelated\n\nNothing about deployment here at all.\n", encoding="utf-8")
        s1, _ = score_file(c1, terms("部署 失败"), 20)
        s2, _ = score_file(c2, terms("部署 失败"), 20)
        ok = s1 > 0 and s2 == 0  # 相关文件得分>0；无关文件零命中=0 分
        c1.unlink(); c2.unlink(); base.rmdir()  # 语料与父目录全清，不留残骸
        print("selftest:", "PASS" if ok else "FAIL", f"(相关={s1:.2f} 无关={s2:.2f})")
        return 0 if ok else 1

    q = " ".join(args.query).strip()
    if not q:
        ap.error("需要查询词")
    q_terms = terms(q)
    root = Path(args.root)
    files = list(iter_files(root, args.glob))
    if not files:
        print("无命中（根目录下没有匹配文件——分辨：路径没对上）")
        return 0
    scored = []
    for p in files:
        s, hits = score_file(p, q_terms, avg_len=200)
        if s > 0:
            scored.append((s, p, hits))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("无命中（0 个文件得分 >0）——按纪律分辨：确实没有 / 换词再试（检索三连）/ Tags 缺失")
        return 0
    for s, p, hits in scored[:args.top]:
        rel = p.relative_to(root) if p.is_relative_to(root) else p
        print(f"{s:7.2f}  {rel}")
        for ln, text in hits:
            print(f"        L{ln}: {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
