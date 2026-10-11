# DESIGN.md — super-memory 宣传页设计契约

> 品牌人格：权威专家 · 情绪板：笔记 + 书页 + 温度 · 参考：GitHub（结构感）但仅亮色 · 禁忌：卡片网格堆砌、居中大标题 Hero、蓝紫系、emoji 图标
> 形态隐喻：**学者档案卷宗**——暖白纸面、衬线标题、编号章节（一/二/三）、朱砂仅做标记与索引、左侧目录随滚动点亮。

## 1. 视觉主题与氛围

纸面档案感：像一本被认真维护的项目卷宗，而非营销落地页。克制、可信、有温度。
情绪关键词：笔记 · 书页 · 秩序。禁止任何渐变 Hero、卡片网格、居中大标题。

## 2. 配色（仅亮色，纸面系）

```css
:root {
  --color-paper: #faf7f0;        /* 页面底 · 暖白纸 */
  --color-paper-deep: #f1ecdf;   /* 代码/元信息底 · 深一阶纸 */
  --color-ink: #26221c;          /* 正文墨色（暖黑） */
  --color-ink-faint: #6e6659;    /* 次要文字 · 淡墨 */
  --color-line: #dcd5c4;         /* 规则线 · 纸纹分隔 */
  --color-accent: #a13d2d;       /* 朱砂 · 编号/链接/当前章节标记 */
  --color-accent-deep: #7c2d21;  /* 朱砂 hover */
}
```

## 3. 排版

```css
:root {
  --font-display: Georgia, "Times New Roman", "Noto Serif SC", "Source Han Serif SC", SimSun, serif;
  --font-body: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, Consolas, "JetBrains Mono", monospace;
  --font-size-hero: clamp(30px, 4.5vw, 42px);
  --font-size-h2: 24px;
  --font-size-body: 16px;
  --font-size-meta: 13px;
  --line-height-body: 1.85;
}
```
标题衬线（--font-display），正文无衬线，代码/标识符等宽。字重克制：display 用常规字重靠字号立层次，最多 600。

## 4. 间距

```css
:root {
  --space-section: 76px; --space-block: 28px; --space-inline: 20px;
  --measure: 700px;      /* 正文栏宽（书页行长约 35em） */
}
```

## 5. 布局与构图

- 单栏书页（正文 max-width --measure），桌面端左侧固定小目录（≥1080px 显示，随滚动点亮当前节）
- **禁居中大标题**：卷首左对齐——眉题小字 → 衬线大标题 → 首段 → 元信息行（真实指标）
- **禁卡片网格**：信息用编号章节（一/二/三）、条目列表（条目号 + 名称 + 描述）、表格承载；分隔靠规则线与小节间距
- 全局响应式：≤1080px 目录隐藏；≤640px 字号降档、流程图纵向

## 6. 组件

- 章节编号：朱砂色衬线大字（一/二/三…），随滚动由淡墨转朱砂
- 条目：无底色，仅条目号 + 规则线底边
- 代码块：--color-paper-deep 底 + 墨字 + 左侧 2px 规线（不用深色块）
- 表格：仅横线（上下粗规线 + 行间细线），无竖线无斑马纹
- 所有交互元素必须含 :focus-visible 样式

## 7. 动效与交互

滚动叙事（中等偏慢、仪式感）：
- 章节进入视口：编号淡墨 → 朱砂（IntersectionObserver，250ms）
- 统计数字进入视口计数到目标值（800ms，ease-out）
- `prefers-reduced-motion: reduce` 时全部动效关闭，直接呈现终态
仅用原生 JS（≤40 行），无外部依赖。

## 8. 语调与品牌

权威专家 × 笔记温度：文案写实、无营销形容词、指标全部真实（18/18 评测、33 提交、40 项目实测）；语气像一份维护良好的卷宗的前言。

## 9. 禁止模式

蓝紫渐变与 AI 默认色系（#4f46e5/#6366f1/#8b5cf6 等）· emoji 作图标 · 居中大标题 Hero ·
卡片网格堆砌 · 灰底白卡 · 假指标 · lorem ipsum · 装饰 blob/wave · 深色代码块以外的深色大块 · 多方向混搭。

Font labels for catalog extraction: serif-display-georgia / sans-body-system / mono-consolas
