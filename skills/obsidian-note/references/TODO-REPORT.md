# Todo Report

Triggered when user asks: *"what's on my todo?"*, *"show my tasks"*, *"what do I need to do?"*

## Step 1 — Search whole vault for open todos

```bash
obsidian tasks todo verbose
```

This is mandatory for todo reports. It returns a flat list of all incomplete `- [ ]` tasks from every note in the vault.

To separately isolate in-progress items (custom status):
```bash
obsidian tasks status="/" verbose
```

---

## Step 2 — Filter out wishlist and shopping items

Get the wishlist task set to exclude precisely:
```bash
obsidian tasks todo path="Personal/🛒 Wishlist.md" verbose
```

Discard any task whose source file matches this path. Additionally skip these content signals:
- Shopping URLs (e.g. `olx.ua`, `amazon`, `aliexpress`, `decathlon.ua`, `epicentrk.ua`, `terraincognita.com.ua`, `capricorn.com.ua`, `4camping.com.ua`)
- Physical product names (gear, clothing, gadgets, appliances, furniture)
- Financial savings goals with ₴/$ amounts tied to property/investments
- Wishes unrelated to actionable development (e.g. "Побудувати дім…")

Keep: certifications, dev tasks, work tasks, personal health/growth actions, project tasks, ideas with due dates.

## Step 3 — Group tasks by topic

| Topic | Signals |
|-------|---------|
| **⚠️ Overdue / Due Soon** | `📅` date today or in the past — extract to top section regardless of topic |
| **ARB / Al-Rajhi Bank** | "ARB", "WebKul", "marketplace", "Magento", "git workflow", "runbook", "Max", "contract", "ARBBI" |
| **SunnyEurope** | "Sunny", "SunnyEurope", "runbook", "UAT", "SUNNYR", "deploy" |
| **SwissSense / AI Advisor** | "SwissSense", "AI advisor", "PoC", "Vertex", "Gemini", "MCP", "Alokai", "Cloud Run", "KPI", "chat widget" |
| **Vaimo / General Work** | "Vaimo", "QBR", "onboarding", "presentation", "architect", "Ivan", "Bartosz", general work ideas |
| **Dev / Tools** | CLI, coding tools, certifications, `.gitmessage`, `node`, Copilot, skills, MCPs, GitHub |
| **Personal** | health ("зуби", "себорея", "мізинець", "пробіжка"), language learning, certifications, life goals, HiBob |

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
