import re, glob, os, json, sys, subprocess

BS = chr(92)


def norm(p):
    return p.replace(BS, "/")


def body(p):
    raw = open(p, encoding="utf-8").read()
    m = re.match(r"^---\r?\n.*?\r?\n---\r?\n", raw, re.S)
    return raw[m.end():].encode() if m else raw.encode()


skill_files = ["SKILL.md"] + sorted(glob.glob("subskills/*/SKILL.md"))
ref_files = sorted(glob.glob("references/*.md"))

print("=== 体积：SKILL.md 正文 8000B 上限 ===")
over = []
for p in skill_files:
    n = len(body(p))
    if n > 8000:
        over.append(p)
    print("  %-34s %6dB %s" % (p, n, "ok" if n <= 8000 else "OVER"))
print("  超限:", over or "无")
for p in ref_files:
    print("  %-34s %6dB (reference,不受限)" % (p, os.path.getsize(p)))

print("=== 引用链接解析 ===")
bad = []
for p in skill_files:
    txt = open(p, encoding="utf-8").read()
    for ref in set(re.findall(r"(?:\.\./)*(?:references|subskills)/[\w.\-]+\.md", txt)):
        if ref.startswith(".."):
            t = os.path.normpath(os.path.join(os.path.dirname(p), ref))
        else:
            t = ref
        if not os.path.exists(t):
            bad.append((p, ref))
print("  断链:", bad or "无")

print("=== 残留违规 ===")
checks = {
    "宿主硬编码(非探测表)": r"\.claude/projects/\[project\]|\.claude/projects/<project>",
    "花括号路径变量": r"\$\{?SKILL_DIR|\$\{?CLAUDE_SKILL_DIR",
}
allf = skill_files + ref_files
for k, pat in checks.items():
    hits = [(p, i + 1) for p in allf for i, l in enumerate(open(p, encoding="utf-8")) if re.search(pat, l)]
    print("  %s: %d %s" % (k, len(hits), hits[:4]))

print("=== frontmatter ===")
raw = open("SKILL.md", encoding="utf-8").read()
m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", raw, re.S)
fm = m.group(1)
print("  字段:", re.findall(r"^(\w[\w-]*):", fm, re.M))
print("  frontmatter 字符数:", len(fm), "(上限 1024)")
print("  description 里含工作流箭头:", "->" in fm or "→" in fm)
print("  description 里含'合并来源':", "合并来源" in fm)

print("=== evals ===")
d = json.load(open("evals/evals.json", encoding="utf-8"))
kinds = {}
for c in d["cases"]:
    kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
print("  用例:", len(d["cases"]), kinds)
sts = {}
for c in d["cases"]:
    sts[c["status"]] = sts.get(c["status"], 0) + 1
print("  状态分布:", sts, "| 未实跑残留:", sts.get("not_executed", 0))

print("=== 结构最小要求 ===")
for need in ["SKILL.md", "evals/evals.json"]:
    print("  %-20s %s" % (need, "存在" if os.path.exists(need) else "缺失"))

print("=== handoff 专项 ===")
codes = ["[V]", "[W]", "[Q]", "[R]", "[F]"]
hs = open("subskills/handoff/SKILL.md", encoding="utf-8").read()
print("  五个置信度码齐且互不重复:", all(c in hs for c in codes),
      "| 码数:", len(set(codes)), "| 无符号重叠:", len(set(c.split()[0] for c in codes)) == 5)
is_ = open("subskills/intake/SKILL.md", encoding="utf-8").read()
print("  handoff 指向 intake:", "ok" if "intake" in hs else "❌ 缺")
print("  handoff 进度可扫读质量条:", "ok" if "进度可扫读" in hs else "❌ 缺")
print("  handoff 快照即头部质量条:", "ok" if "快照即头部" in hs else "❌ 缺")
print("  handoff 压缩保全分级:", "ok" if "压缩保全" in hs else "❌ 缺")
print("  intake 五码齐:", "ok" if all(c in is_ for c in codes) else "❌ 缺")
print("  intake 引用 discovery/scaffold:", "ok" if "intake-memory-discovery" in is_ and "intake-scaffold" in is_ else "❌ 缺")
print("  intake 全面分析+三角验证+newermt:",
      "ok" if all(k in is_ for k in ["全面分析", "新鲜度三角", "newermt"]) else "❌ 缺")
disc = open("references/intake-memory-discovery.md", encoding="utf-8").read()
print("  discovery 全面分析三层次+实战案例:", "ok" if "全面分析三层次" in disc and "33 个提交" in disc else "❌ 缺")

tpl = open("references/handoff-template.md", encoding="utf-8").read()
secs = re.findall(r"^## \*?\u2605?\*?(\d+)\.", tpl, re.M)
print("  模板节数:", len(secs), "期望 11 ->",
      "ok" if len(secs) == 11 else "MISMATCH", secs)
sec_stars = re.findall(r"^## \u2605\d+\.", tpl, re.M)
print("  必需节标记(★)个数:", len(sec_stars), "期望 7 ->",
      "ok" if len(sec_stars) == 7 else "MISMATCH")
print("  §0 当前快照存在:", "ok" if "## \u26050. 当前快照" in tpl else "❌ 缺")
print("  快照七槽位齐:", "ok" if all(k in tpl for k in ["**目标**", "**需求与约束**", "**关键决策**", "**状态**", "**下一步动作**", "**相关文件**", "**关键上下文**"]) else "❌ 缺")
print("  图例存在:", "ok" if "★ = 必需节" in tpl else "缺失")

print("=== A5 统计命令 vs 黄金样本（防'命令与格式脱节'复发）===")
golden_handoff = "- `[V]` `src/x/y.ts:42` 做了什么 — 要点 — 验证：npm test"
golden_knowledge = "**置信度**：[V]　　**生效**：2026-10-01　　**记录**：2026-10-03　　**最后验证**：2026-10-03　　**适用版本**：main" \
                   "\n**Related**：K-20261001-001"
pats = set(re.findall(r'grep -[a-zA-Z]+E "([^"]+)"', hs))
hit_h = [p for p in sorted(pats) if re.search(p, golden_handoff)]
hit_k = [p for p in sorted(pats) if re.search(p, golden_knowledge)]
print("  HANDOFF 黄金样本:", "命中" if hit_h else "❌ 0 命中", hit_h[:2])
print("  长期库黄金样本:", "命中" if hit_k else "❌ 0 命中", hit_k[:2])
print("  黄金样本整体:", "ok" if hit_h and hit_k else "FAIL")

tiers = open("references/knowledge-tiers.md", encoding="utf-8").read()
spots = [".learnings/", ".ai/HANDOFF.md", ".ai/knowledge/", "agent 记忆库", "规则文件"]
missing = [s for s in spots if s not in tiers]
print("  五处落点全覆盖:", "ok" if not missing else missing)
print("  格式字段齐(生效/记录/Related):", "ok" if all(s in tiers for s in ["**生效**", "**记录**", "**Related**"]) else "缺字段")
print("  巩固四操作齐:", "ok" if all(s in tiers for s in ["ADD", "UPDATE", "SUPERSEDE", "NOOP"]) else "缺")
print("  last_verified 超龄规则:", "ok" if "90 天" in tiers and "last_verified" in tiers else "缺")

print("=== 寻址与编号规范 ===")
addr = open("references/memory-addressing.md", encoding="utf-8").read()
print("  通用探测含 dotglob:", "ok" if "dotglob" in addr else "❌ 缺")
print("  多命中裁决顺序:", "ok" if "裁决顺序" in addr else "❌ 缺")
print("  K-NNN 生成命令:", "ok" if "K-$D" in tiers and "wc -l" in tiers else "❌ 缺")
print("  knowledge 淘汰不隔离:", "ok" if "不隔离" in tiers else "❌ 缺")
print("  失效标记三要素示例:", "ok" if "**已失效**：" in tiers and "取代者 ID + 原因" in tiers else "❌ 缺")
print("  知识库索引登记规则:", "ok" if "登记一行" in tiers else "❌ 缺")
print("  共存纪律（重读+分工）:", "ok" if "编辑前重读" in addr and "它铺叙事" in addr else "❌ 缺")

print("=== 检索与可选件 ===")
r = subprocess.run([sys.executable, "scripts/search.py", "--selftest"],
                   capture_output=True, text=True)
st = r.stdout.strip()
print("  search.py selftest:", st if "PASS" in st else "❌ " + (st or r.stderr.strip())[:60])
cap = open("subskills/capture/SKILL.md", encoding="utf-8").read()
print("  capture Tags 字段:", "ok" if "- Tags: " in cap else "❌ 缺")
print("  K 条目 Tags 行:", "ok" if "**Tags**：" in tiers else "❌ 缺")
print("  intake 检索三连:", "ok" if "换词三连" in is_ else "❌ 缺")
doc = open("references/memory-doctor.md", encoding="utf-8").read()
print("  doctor 锚点活性(第五项):", "ok" if "锚点活性" in doc and "检查五" in doc else "❌ 缺")
hooks = open("references/hooks-setup.md", encoding="utf-8").read()
print("  hooks 四时机(PostToolUse+session_intro):",
      "ok" if "PostToolUse" in hooks and "hook_session_intro" in hooks and "hook_capture_reminder" in hooks else "❌ 缺")
print("  可选件文档齐(memory-git/semantic-search):",
      "ok" if os.path.exists("references/memory-git.md") and os.path.exists("references/semantic-search.md") else "❌ 缺")

parent = open("SKILL.md", encoding="utf-8").read()
subs = sorted(glob.glob("subskills/*/SKILL.md"))
print("  子命令目录数:", len(subs), [os.path.basename(os.path.dirname(p)) for p in subs])
notrouted = [p for p in subs if norm(p) not in parent.replace(BS, "/")]
print("  未在主入口路由表中出现的子技能:", notrouted or "无")
for kw in ["handoff", "intake", "[V]", "knowledge-tiers"]:
    print("  主入口提到 %s: %s" % (kw, kw in parent))

print("  用例总数:", len(d["cases"]))
