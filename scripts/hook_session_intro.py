#!/usr/bin/env python3
"""SessionStart hook：存在 .ai/HANDOFF.md 时，抽取 §0 当前快照注入开场（super-memory 可选安装件）。

无 HANDOFF、无 §0 时静默退出（旧式文档由 intake 读取端处理）。
"""
import sys
from pathlib import Path


def main():
    h = Path(".ai") / "HANDOFF.md"
    if not h.exists():
        return 0
    out, on = [], False
    try:
        lines = h.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return 0
    for line in lines:
        if line.startswith("## ★0"):
            on = True
            out.append(line)
            continue
        if on and line.startswith("## "):
            break
        if on:
            out.append(line)
    body = "\n".join(out).strip()
    if body:
        print("[super-memory] §0 当前快照（源自 .ai/HANDOFF.md，详情走 intake 接手流程）：")
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
