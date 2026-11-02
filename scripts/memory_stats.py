#!/usr/bin/env python3
"""memory-stats — super-memory 健康面板。

统计全部记忆位的条目数、类型分布、超龄、Tags 覆盖——帮你决定哪些记忆值得保留。

用法:
  python scripts/memory_stats.py                 # 当前目录的记忆
  python scripts/memory_stats.py --auto          # 自动枚举全部记忆位（含宿主）

设计约束：纯标准库、只读、不修改任何文件。
支持两种条目格式：## [ID] 块式 + frontmatter 文件式。
"""
import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

STALE_DAYS = 90
NOISE = ("/node_modules/", "/.git/", "/.mimosa/", "/__pycache__/",
         "/opensource-reference/")
FM_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.S | re.M)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _md_files(root: Path):
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*.md")):
        s = p.as_posix()
        if any(n in f"/{s}" for n in NOISE):
            continue
        yield p


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _dates(t: str) -> list:
    return [datetime.strptime(m, "%Y-%m-%d")
            for m in DATE_RE.findall(t)
            if len(m) == 10]


def _count_entries(root: Path) -> dict:
    """统计一个记忆位：返回 entries/by_type/stale/no_tags/newest/oldest。"""
    s = {"entries": 0, "by_type": Counter(), "stale": 0,
         "no_tags": 0, "newest": None, "oldest": None, "files": 0}
    cutoff = datetime.now() - timedelta(days=STALE_DAYS)
    for p in _md_files(root):
        if p.name == "MEMORY.md":
            continue
        t = _read(p)
        if not t.strip():
            continue
        s["files"] += 1
        # 提取日期（从 frontmatter last_verified 或正文 最后验证/生效/记录）
        dates = _dates(t)
        if dates:
            newest_file = max(dates)
            if s["newest"] is None or newest_file > s["newest"]:
                s["newest"] = newest_file
            if s["oldest"] is None or newest_file < s["oldest"]:
                s["oldest"] = newest_file
            # 超龄判定：文件内最旧的日期超 90 天
            if (datetime.now() - min(dates)).days > STALE_DAYS:
                s["stale"] += 1
        # 条目计数：块式 ## [ID] 或 frontmatter 独立文件
        blocks = re.findall(r"^## \[[A-Z]+-\d{8}-\d+\]", t, re.M)
        has_fm = FM_RE.match(t) and "name:" in t
        if blocks:
            s["entries"] += len(blocks)
            for b in blocks:
                prefix = re.search(r"\[([A-Z]+)-", b)
                if prefix:
                    s["by_type"][prefix.group(1)] += 1
        elif has_fm:
            s["entries"] += 1
            tp = re.search(r"type:\s*(\w+)", t)
            if tp:
                s["by_type"][tp.group(1)] += 1
        # Tags 检查
        if "## [" in t and "Tags" not in t and "tags" not in t:
            s["no_tags"] += 1
    return s


def auto_roots(cwd: Path) -> list[tuple[Path, str]]:
    """枚举全部记忆位（项目相对 + 宿主用户目录）。"""
    home = Path.home()
    roots, seen = [], set()

    def add(p, label):
        rp = p.resolve().as_posix()
        if p.is_dir() and rp not in seen:
            seen.add(rp)
            roots.append((p, label))

    # 项目相对
    for rel in (".ai", ".learnings", "memory", ".memory",
                ".workbuddy/memory", ".claude/memory", ".codex-memory"):
        add(cwd / rel, rel)
    # 宿主用户级 + 项目级
    for pat, label in (
        (".qoder/memory", "qoder:用户级"),
        (".qoder/projects/*/memory", "qoder:项目级"),
        (".zcode/cli/memories/projects/*/memory", "zcode"),
        (".claude/memory", "claude"),
        (".workbuddy/memory", "workbuddy"),
        (".codex/memories", "codex"),
    ):
        if "*" in pat:
            for p in sorted(home.glob(pat)):
                if p.is_dir():
                    add(p, f"{label}:{p.parent.name[:20]}")
        else:
            add(home / pat, label)
    return roots


def report(stats_list: list[dict]):
    total_e = sum(s["entries"] for s in stats_list)
    total_stale = sum(s["stale"] for s in stats_list)
    total_no_tags = sum(s["no_tags"] for s in stats_list)
    print(f"\n{'═' * 52}")
    print(f"  super-memory 健康面板  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'═' * 52}")
    print(f"  总条目: {total_e} · 记忆位: {len(stats_list)} · 超龄: {total_stale} · 缺Tags: {total_no_tags}")
    print()
    for s in stats_list:
        line = f"  {s['label']:<30} {s['entries']:>3} 条"
        if s["stale"]:
            line += f" · 超龄 {s['stale']}"
        if s["no_tags"]:
            line += f" · 缺Tags {s['no_tags']}"
        if s["by_type"]:
            types = " ".join(f"{k}:{v}" for k, v in s["by_type"].most_common(4))
            line += f"  [{types}]"
        print(line)
    print()
    print("  建议：超龄→重验或降级 · 缺Tags→补中英文 · 重复→四操作合并 · 全走 neat")
    print(f"{'═' * 52}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="super-memory 健康面板")
    ap.add_argument("--root", default=".", help="项目根目录")
    ap.add_argument("--auto", action="store_true", help="枚举全部记忆位")
    args = ap.parse_args(argv)

    cwd = Path(args.root).resolve()
    roots = auto_roots(cwd) if args.auto else [(cwd, cwd.name)]
    stats_list = []
    for root, label in roots:
        s = _count_entries(root)
        if s["files"] > 0:
            s["label"] = label
            stats_list.append(s)
    if not stats_list:
        print("无记忆文件")
        return 0
    report(stats_list)
    return 0


import sys
if __name__ == "__main__":
    sys.exit(main())
