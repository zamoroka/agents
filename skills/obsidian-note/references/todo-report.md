# Todo Report

Triggered when the user asks for an overview of open tasks — phrasings vary:
*"what's on my todo?"*, *"show my tasks"*, *"what do I need to do?"*,
*"what's on my plate"*, *"dump my list"*, *"focus me"*.

_Why this stays an LLM workflow (not a script): the value here is **judgment** — deciding which topic a task belongs to, whether it's still worth surfacing, and how to phrase the grouping for the current ask. A keyword script would either miss new projects/topics or mis-classify tasks the user has phrased  differently. The model can read all the signals (path, tags, surrounding text) and apply real understanding._

## Step 1 — Search whole vault for open todos

```bash
obsidian tasks todo verbose
```

Mandatory for todo reports. Returns a flat list of all incomplete `- [ ]` tasks from every note in the vault.

To separately isolate in-progress items (custom status):

```bash
obsidian tasks status="/" verbose
```

## Step 2 — Filter out wishlist and shopping items

`Personal/🛒 Wishlist.md` holds shopping intent, not actionable work — if it shows up in the report it buries real tasks. Drop:

- Any task whose source file is under `Personal/🛒 Wishlist.md` (or other shopping-themed notes — judge by file path).
- Tasks that are clearly shopping intent regardless of file: physical products (gear, clothing, gadgets, appliances, furniture), shopping URLs (olx, amazon, aliexpress, decathlon, epicentrk, rozetka, etc — these are **examples**, not an exhaustive list), price/savings goals tied to property or investments, life-wish entries unrelated to actionable development (e.g. "Побудувати дім…", "купити нову куртку").

Keep: certifications, dev tasks, work tasks, personal health/growth actions, project tasks, ideas with due dates.

If a task is ambiguous (could be wishlist or could be a real action item), err on the side of keeping it — the user can ignore false positives, but a silently-dropped real task is invisible.

## Step 3 — Group tasks by topic

Group by the project or area the task belongs to. The table below lists the **current** active topics with a few example signals — these are not exhaustive keyword filters, they are starting points for judgment. A task that doesn't mention any listed signal but is clearly about ARB (e.g. references "Mohammed" or "the cutover") still goes under ARB. Likewise, if a new project appears in the vault that isn't listed here, add a new section for it.

| Topic | Example signals (not exhaustive) |
|-------|----------------------------------|
| **⚠️ Overdue / Due Soon** | `📅` date today or in the past — pull to top section regardless of topic |
| **ARB / Al-Rajhi Bank** | ARB, WebKul, marketplace, Magento, Max, Mohammed, ARBBI, runbook, contract |
| **SunnyEurope** | Sunny, SunnyR, UAT, deploy, runbook |
| **SwissSense / AI Advisor** | SwissSense, AI advisor, PoC, Vertex, Gemini, MCP, Alokai, Cloud Run, chat widget |
| **Vaimo / General Work** | Vaimo, QBR, onboarding, presentation, architect, EME, Ivan, Bartosz |
| **Dev / Tools** | CLI, Copilot, skills, MCPs, GitHub, `.gitmessage`, node, certifications |
| **Personal** | health (зуби, себорея, мізинець, пробіжка), language learning, HiBob, life goals |

Tag overlap also helps — `obsidian tags file="<task source>"` can confirm a topic when the text alone is ambiguous.

Assign to the most specific topic when a task fits multiple. Skip empty or meaningless tasks.

## Step 4 — Sort within each group

1. **Priority** (highest first): 🔺 → ⏫ → 🔼 → 🔽 → ⏬ → _(none)_
2. **Due date** — `📅 YYYY-MM-DD` tasks first, soonest first
3. **No date** — after dated tasks, in original order

## Step 5 — Render the report

```
## ⚠️ Overdue / Due Soon
- 🔺 Task text 📅 2026-04-06

## ARB / Al-Rajhi Bank
- 🔺 Task text 📅 2026-04-17
- Task text
- 🔽 Task text

## SunnyEurope
...
```

Rules: keep original task text and emojis intact; show `📅` inline after text; omit empty sections; no section for skipped wishlist items.
