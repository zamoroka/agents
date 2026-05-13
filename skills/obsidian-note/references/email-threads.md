# Email Threads

Use this reference when the user asks to save an email thread, forwarded/replied email chain, or project communication where headers like `Subject`, `From`, `To`, `Cc`, and `Date` are present.

## Goal

Preserve the real email content, but make the note readable as a wiki page. Treat cleanup as structure cleanup, not rewriting.

_Why this distinction matters: the user often comes back to email threads to verify what was actually said (legal, commercial, technical commitments). If wording drifts, the note becomes useless as a record._

## Placement

- Put client/project email threads under the relevant project `Communications/` folder when it exists or when the user names it.
- For ARB, use `Work/Vaimo/projects/ARB/Communications/`.
- Filename starts with the earliest thread date in `YYYY-MM-DD` format, followed by a concise subject-based title.
- If creating a new `Communications/` folder, update `AGENTS.md` vault structure.

## Frontmatter

Use normal wiki frontmatter:

- `updated`: current datetime
- `tags`: folder tags plus `communication`, `email-thread`, project tag, and people tags for meaningful participants
- `related`: project README and TASKS when relevant
- `summary`: one short sentence describing the thread purpose

## Structure

Use this shape:

```markdown
# YYYY-MM-DD Short Thread Title

**Subject:** Original subject

## Email 1: <date>

**From:** Sender <email>
**To:** Recipient <email>
**Cc:** Recipients <email>
**Date:** Original date

> Main email body.
> Keep the salutation, body, and lists here.

Thank you.
Best Regards,
Sender Name
Sender Role

---

## Email 2: <date>
...
```

Rules:

- Flatten quoted replies into separate email blocks.
  _Why: nested quotes make threads unreadable on the third or fourth reply. Each email as its own block lets the user scan the conversation linearly._
- Order blocks chronologically when the thread makes that clear.
- Keep `From`, `To`, `Cc`, and `Date` for each email when available.
- Use `---` between email blocks.
- Mark the main email body with markdown blockquote markers (`>`), including salutation, body, and lists.
  _Why: the blockquote visually separates "what was said" from metadata and signatures, and makes the message robust to future re-rendering or extraction._
- Keep sign-off lines like `Regards`, `Thank you`, and `Best Regards` outside the blockquote together with cleaned signature name/title lines.
- Keep email metadata outside the blockquote.
- Do not keep nested quote wrappers or `On <date>, <person> wrote:` wrapper lines after flattening.
- Keep the original subject once near the top.

## Cleanup Allowed

Allowed cleanup:

- Remove inline image placeholders and logo-only attachments.
- Remove email footer noise: legal disclaimers, social links, website links, mailto links, repeated phone/address blocks, and image/logo references.
- Keep sender name and role/title lines in signatures when useful.
- Normalize excessive blank lines around signatures.

Do not change:

- Email body wording.
- Questions, numbered lists, cautions, decisions, or business meaning.
- Sender/recipient/date metadata.

## Task Handling

Do not extract tasks into project `TASKS.md` unless the user asks for task extraction or the email clearly creates an action item and the user did not request content-only preservation. For a preservation request, report that tasks were not extracted.

## Verification

Before finishing, check:

- no `inline-image-placeholder`, logo filenames, or image-only attachment section remains when cleanup was requested
- no nested quote wrappers or `On ... wrote:` wrappers remain after flattening
- main email body lines are marked with `>` while metadata, sign-offs, and cleaned signatures are not
- each email block has the available metadata
- `git diff --check` passes when the vault is under git

## Worked example: forwarded reply → cleaned wiki block

Demonstrates flattening, signature cleanup, and the blockquote rule.

**Input (raw forwarded email body):**

```
---------- Forwarded message ---------
From: Max Schmidt <max.schmidt@arb.example>
Date: Mon, May 4, 2026 at 3:14 PM
Subject: Re: Marketplace cutover — UAT status
To: Pavlo Zamoroka <pavlo.zamoroka@vaimo.com>
Cc: Ivan Bordiuh <ivan@vaimo.com>

Hi Pavlo,

Confirmed — we'll push the cutover by one sprint. Webkul patch is
in our UAT next Tuesday. I'll send updated steerco slides EOD.

Best Regards,
Max Schmidt
Head of Digital, ARB
[inline-image: arb-logo.png]
www.arb.example | Legal disclaimer: This email is confidential…

On Mon, May 4, 2026 at 10:02 AM, Pavlo Zamoroka <pavlo.zamoroka@vaimo.com> wrote:
> Hi Max,
>
> Heads up — Webkul confirmed the rounding errors are in their core. ETA
> ~2 weeks. I want to push the cutover to next sprint. OK with you?
>
> Thanks,
> Pavlo
```

**Output (cleaned wiki block):**

```markdown
# 2026-05-04 Marketplace cutover — UAT status

**Subject:** Marketplace cutover — UAT status

## Email 1: 2026-05-04 10:02

**From:** Pavlo Zamoroka <pavlo.zamoroka@vaimo.com>
**To:** Max Schmidt <max.schmidt@arb.example>
**Date:** Mon, May 4, 2026 at 10:02 AM

> Hi Max,
>
> Heads up — Webkul confirmed the rounding errors are in their core. ETA
> ~2 weeks. I want to push the cutover to next sprint. OK with you?

Thanks,
Pavlo

---

## Email 2: 2026-05-04 15:14

**From:** Max Schmidt <max.schmidt@arb.example>
**To:** Pavlo Zamoroka <pavlo.zamoroka@vaimo.com>
**Cc:** Ivan Bordiuh <ivan@vaimo.com>
**Date:** Mon, May 4, 2026 at 3:14 PM

> Hi Pavlo,
>
> Confirmed — we'll push the cutover by one sprint. Webkul patch is
> in our UAT next Tuesday. I'll send updated steerco slides EOD.

Best Regards,
Max Schmidt
Head of Digital, ARB
```

What changed:
- Nested quoted reply hoisted to its own block (Email 1), chronological order
- Inline image placeholder, legal disclaimer, and website link removed from signature
- `From`/`To`/`Cc`/`Date` kept verbatim per block
- Body wrapped in `>` blockquote; sign-offs and signature kept outside
- `On <date>, <person> wrote:` wrapper dropped after flattening
- Subject kept once at the top, not repeated per block
