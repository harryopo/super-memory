#!/usr/bin/env python3
"""PostToolUse hook：Bash 命令失败时提醒 capture（super-memory 可选安装件）。

stdin 收宿主 hook JSON；判定失败（success=False 或非零 exit code）时向 stdout
输出一行提醒（exit 0，提醒进入 agent 上下文）。解析失败一律静默放行。
"""
import json
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if (data.get("tool_name") or "") != "Bash":
        return 0
    resp = data.get("tool_response")
    failed = False
    if isinstance(resp, dict):
        if resp.get("success") is False:
            failed = True
        else:
            code = resp.get("exit_code", resp.get("code"))
            if isinstance(code, int) and code != 0:
                failed = True
    elif isinstance(resp, str):
        low = resp.lower()
        if "exit code" in low and "exit code 0" not in low:
            failed = True
    if failed:
        print("[super-memory] 命令失败——若属错误/纠正，按 capture 落盘（.learnings/ERRORS.md）再继续；已记则忽略本提醒。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
