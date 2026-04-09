# Todo Report

Triggered when the user asks about their tasks, todos, or "what do I need to do".

## Step 1 — Fetch all tasks

```bash
obsidian tasks todo
```

This returns a flat list of all incomplete `- [ ]` tasks from every note in the vault.

---

## Step 2 — Filter out wishlist and shopping items

Skip any task that originates from or clearly belongs to `Personal/🛒 Wishlist.md`.

**Signals to exclude a task:**
- Contains a shopping URL (e.g. `olx.ua`, `4camping.com.ua`, `decathlon.ua`, `amazon`, `aliexpress`, `epicentrk.ua`, `terraincognita.com.ua`, `capricorn.com.ua`)
- Is a physical product name (gear, clothing, gadgets, appliances, furniture)
- Is a financial savings goal tied to property/investments with ₴/$ amounts
- Is clearly a wish or aspiration unrelated to actionable work/personal development (e.g. "Побудувати дім…")

**Keep:** certifications, dev tasks, work tasks, personal health/growth actions, project tasks, ideas with due dates.

---

## Step 3 — Group tasks by topic

Infer the topic from task content using these signals:

| Topic | Signals |
|-------|---------|
| **⚠️ Overdue / Due Soon** | `📅` date that is today or in the past; extract to a top section regardless of other topic |
| **ARB / Al-Rajhi Bank** | "ARB", "WebKul", "marketplace", "Magento", "git workflow", "runbook", "Max", "contract", "ARBBI" |
| **SunnyEurope** | "Sunny", "SunnyEurope", "runbook", "UAT", "SUNNYR", "deploy" |
| **SwissSense / AI Advisor** | "SwissSense", "AI advisor", "PoC", "Vertex", "Gemini", "MCP", "Alokai", "Cloud Run", "KPI", "chat widget" |
| **Vaimo / General Work** | "Vaimo", "QBR", "onboarding", "presentation", "architect", "Ivan", "Bartosz", general work ideas |
| **Dev / Tools** | CLI, coding tools, certifications, `.gitmessage`, `node`, Copilot, skills, MCPs, GitHub |
| **Personal** | health ("зуби", "себорея", "мізинець", "пробіжка"), language learning, certifications, life goals, HiBob |

If a task fits multiple topics, assign to the most specific one.
If a task is empty or has no meaningful content, skip it.

---

## Step 4 — Sort within each group

Within each topic group, order tasks by:

1. **Priority** (highest first):

   | Emoji | Priority |
   |-------|----------|
   | 🔺 | Highest |
   | ⏫ | High |
   | 🔼 | Medium |
   | _(none)_ | Normal |
   | 🔽 | Low |
   | ⏬ | Lowest |

2. **Due date** — tasks with `📅 YYYY-MM-DD` before tasks without; soonest date first
3. **No date** — append after dated tasks, in original order

---

## Step 5 — Render the report

Output a clean, readable markdown report:

```
## ⚠️ Overdue / Due Soon
- 🔺 Task text 📅 2026-04-06
- Task text 📅 2026-04-07

## ARB / Al-Rajhi Bank
- 🔺 Task text 📅 2026-04-17
- Task text
- 🔽 Task text

## SunnyEurope
...
```

**Rules:**
- Keep the original task text and emojis intact (do not rewrite)
- Show `📅 YYYY-MM-DD` inline after the task text
- Omit empty sections (no heading if no tasks in that group)
- Do not show a section for skipped wishlist/shopping items
