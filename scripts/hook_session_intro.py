#!/usr/bin/env python3
"""SessionStart hook：开场注入 §0 当前快照 + 自上次会话以来的增量摘要。

输出三段（全部有则打印，无则静默——hook 静默 = 宿主无记忆位，正常态）：
  1. §0 当前快照（.ai/HANDOFF.md 的 ★0/§0 块，七槽位）
  2. 记忆增量：近 7 天有改动的记忆文件（.ai/ .learnings/ memory/ .workbuddy/memory/）
  3. git 近况：最近 3 条提交（仅当 .git 存在）

纪律：只读、有界（head 截断）、解析失败静默退出 0——hook 绝不阻断会话启动。
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

MAX_LINES = 16
DAYS = 7
MEMORY_DIRS = (".ai", ".learnings", "memory", ".memory", ".workbuddy/memory")


def snapshot_block() -> list[str]:
    h = Path(".ai") / "HANDOFF.md"
    if not h.exists():
        return []
    out, on = [], False
    try:
        lines = h.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    for line in lines:
        if line.startswith("## ★0") or line.startswith("## §0"):
            on = True
            out.append(line)
            continue
        if on and line.startswith("## "):
            break
        if on:
            out.append(line)
    return out


def recent_memory_files() -> list[str]:
    cutoff = datetime.now() - timedelta(days=DAYS)
    out = []
    for d in MEMORY_DIRS:
        base = Path(d)
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            try:
                mt = datetime.fromtimestamp(p.stat().st_mtime)
                if mt >= cutoff:
                    out.append(f"{p.as_posix()} ({mt:%m-%d %H:%M})")
            except OSError:
                continue
    return out[:MAX_LINES]


def git_recent() -> list[str]:
    if not Path(".git").exists():
        return []
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return []
        return ["git: " + l for l in r.stdout.strip().splitlines()[:3]]
    except (OSError, subprocess.TimeoutExpired):
        return []


def main() -> int:
    try:
        snap = snapshot_block()
        inc = recent_memory_files()
        git = git_recent()
    except Exception:
        return 0  # hook 绝不阻断会话启动
    if not (snap or inc or git):
        return 0
    print("[super-memory] 开场记忆注入")
    if snap:
        print("── §0 当前快照（.ai/HANDOFF.md，详情走 intake）──")
        print("\n".join(snap[:MAX_LINES]))
    if inc:
        print("── 记忆增量（近 %d 天改动的记忆文件）──" % DAYS)
        print("\n".join(inc))
    if git:
        print("── git 近况 ──")
        print("\n".join(git))
    return 0


if __name__ == "__main__":
    sys.exit(main())
