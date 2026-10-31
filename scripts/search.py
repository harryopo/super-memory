#!/usr/bin/env python3
"""memory search — super-memory 的排序检索工具（零依赖，纯标准库）。

对记忆/文档 markdown 做词频加权检索（BM25-lite），中文按字符二元组切词。
比多轮 grep 高效：一次查询返回 Top-N 文件与最佳命中行。

用法:
  python scripts/search.py "查询词 查询词2" [--root 目录] [--top N] [--glob 模式]
  python scripts/search.py "查询词" --auto          # 一次扫全部记忆位（项目位+宿主位）
  python scripts/search.py --selftest

设计约束：纯标准库、无网络、只读。--auto 按 memory-addressing 形态表枚举
项目位（.ai/.learnings/memory/…）与宿主位（~/.qoder、~/.zcode、~/.claude…），
逐库打标签输出——把检索纪律第 0 步（先定库）机械化。
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

# --auto 枚举的记忆位（项目相对 + 用户主目录；与 memory-addressing 形态表同步）
AUTO_PROJECT = (".ai", ".learnings", "memory", ".memory", ".workbuddy/memory",
                ".claude/memory", ".codex-memory", "docs/handoff", "docs/handoffs")
AUTO_USER = (".qoder/memory", ".qoder/projects/*/memory",
             ".zcode/cli/memories/projects/*/memory",
             ".claude/memory", ".workbuddy/memory", ".codex/memories")


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


def auto_roots(cwd: Path, home: Path | None = None) -> list[Path]:
    """枚举全部记忆位（项目相对 + 宿主用户目录），resolve 去重（junction 安全）。"""
    home = Path(home or Path.home())
    roots, seen = [], set()
    for rel in AUTO_PROJECT + AUTO_USER:
        p = (cwd / rel) if not rel.startswith(".qoder/projects") and "*" not in rel else None
        if p is None:
            continue
        rp = p.resolve().as_posix()
        if p.is_dir() and rp not in seen:
            seen.add(rp)
            roots.append(p)
    for rel in AUTO_USER:
        if "*" not in rel:
            continue
        for p in sorted(home.glob(rel)):
            if p.is_dir():
                rp = p.resolve().as_posix()
                if rp not in seen:
                    seen.add(rp)
                    roots.append(p)
    return roots


def main(argv=None):
    ap = argparse.ArgumentParser(description="super-memory 排序检索（BM25-lite）")
    ap.add_argument("query", nargs="*", help="查询词（可多个）")
    ap.add_argument("--root", default=".", help="检索根目录（--auto 时忽略）")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--glob", default=DEFAULT_GLOB)
    ap.add_argument("--auto", action="store_true",
                    help="枚举项目位+宿主位全部记忆库一次扫完（检索纪律第 0 步机械化）")
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
    roots = auto_roots(Path.cwd()) if args.auto else [Path(args.root)]
    files = []
    seen = set()
    for r in roots:
        for p in iter_files(r, args.glob):
            key = p.resolve().as_posix()
            if key not in seen:
                seen.add(key)
                files.append((r, p))
    if not files:
        print("无命中（--auto 未找到任何记忆位——分辨：确实没有 / 形态表没覆盖该宿主）")
        return 0
    scored = []
    for r, p in files:
        s, hits = score_file(p, q_terms, avg_len=200)
        if s > 0:
            tag = r.name if r != Path.cwd() else "."
            scored.append((s, tag, p, hits))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("无命中（0 个文件得分 >0）——按纪律分辨：确实没有 / 换词再试（检索三连）/ Tags 缺失")
        return 0
    for s, tag, p, hits in scored[:args.top]:
        try:
            rel = p.relative_to(Path.cwd()).as_posix()
        except ValueError:
            rel = p.as_posix()
        print(f"{s:7.2f}  [{tag}] {rel}")
        for ln, text in hits:
            print(f"        L{ln}: {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
