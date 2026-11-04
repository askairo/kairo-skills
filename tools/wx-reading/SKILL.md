---
name: wx-reading
description: Chrome 网页版微信读书慢速翻页刷有效时长；处理下一章/下一回、读完重头、结束后按当日有效时长不足 30 分钟补跑一轮。Use when the user wants WeRead web reading time, slow page flips in Chrome weread.qq.com, chapter transitions, or effective-time retry after a session.
---

# wx-reading

Chrome **网页版**微信读书（`weread.qq.com`）慢速翻页，用来刷**有效阅读时长**。不要用微信读书 Mac App 顶替：App 阅读通常不计入网页有效时长口径。

## When to use

- 用户要求在 Chrome 网页版微信读书慢速翻页 / 刷有效阅读
- 会话结束后要核对当日有效时长，不足 30 分钟再补跑
- 章节末出现「下一章 / 下一回」点不动下一页
- 整本书读完需要从头再来

## Boundaries

- Prefer Chrome + `weread.qq.com/web/reader/` only. Never use the Mac WeRead app for 有效阅读.
- Do not start unbounded flip loops. Default one ~30 minute session; at most **one** effective-time retry.
- Login / QR wall → stop and ask the user to scan; do not empty-loop.
- Do not commit or print API keys. `WEREAD_API_KEY` stays in the environment or a secret store.
- Do not modify third-party `weread-skills`; call its gateway docs for `/readdata/detail` only.

## Optional local config

```text
~/.agents/local-config/weread-web-flip/config.json
```

Schema (all optional; no secrets):

```json
{
  "machineId": "<mac-machine-id>",
  "bookTitle": "<book-title>",
  "bookId": "<book-id>",
  "readerUrl": "<reader-url>",
  "helpDir": "<weread-help-dir>",
  "durationMin": 30,
  "dwellMin": 15,
  "dwellMax": 40,
  "effectiveRetryThresholdSec": 1800,
  "binPath": "<path-to-compiled-weread_flip_web>",
  "swiftSource": "<path-to-weread_flip_web.swift>"
}
```

If absent, the calling agent/routine must supply book identity, machine, and paths explicitly.

## Prerequisites

1. At startup, verify `~/.agents/skills/weread-skills/SKILL.md` exists and has a valid `name: weread-skills` frontmatter. If missing, install the official Tencent skill before any WeRead API or reading-stat operation, using the skills-loop installer with source `Tencent/WeChatReading`, path `skills`, name `weread-skills`. Never copy or recreate the official skill manually; never modify its files. If installation fails, stop API-dependent work and tell the user.
2. Read the relevant official `weread-skills` docs before API use. Follow its current version and upgrade instructions (including any `upgrade_info`) before continuing. Reading stats must be queried through this official skill/API workflow, not guessed or replaced with local timers.
3. Target a macOS machine with Google Chrome and Accessibility / Automation permissions for the controlling agent.
4. User is logged into weread.qq.com in Chrome (reader opens without QR).
5. Compiled flip binary, or `swiftc` available to build `scripts/weread_flip_web.swift`.
6. For effective-time checks: `WEREAD_API_KEY` in the environment; never print or persist it.

## Weekly gift-book activity (maximum two books per week)

Use this workflow when the user gives a book title for the weekly reading-to-receive activity:

1. Check the current week's activity page in the logged-in WeRead Chrome session. Read the activity's own eligible-book list, remaining quota, and status; the weekly limit is at most two books. Do not infer the list, week, quota, or completion from memory. Use documented official `weread-skills` APIs where available; otherwise use the visible official activity UI. Do not invent API endpoints or automate undocumented reward calls.
2. Match the user's requested title against the current activity list. If it is not eligible, the list/quota is unavailable, or two weekly rewards have already been used, stop and explain; do not silently substitute another title.
3. Open the matched book in the Chrome reader and assist the user with a **real reading session lasting more than five minutes**. Do not simulate unattended reading, fake engagement, or click/scroll solely to misrepresent that the user read the book. The user must actually read; offer a timer/reminder or keep the book open if needed.
4. Afterward, use the official `weread-skills` reading-progress/stat workflow and the activity UI to verify the required reading duration and reward status. The book is expected to be added automatically; verify it through the official shelf workflow. Do not claim completion merely because five minutes elapsed or the book appears in search.
5. Use the activity UI as the source of truth for weekly quota and reward completion. Keep the two-book maximum; never attempt to bypass eligibility, quota, or activity controls.

## Build / launch the flip binary

Prefer an existing binary from config `binPath` or `<weread-help-dir>/bin/weread_flip_web`. Otherwise compile:

```bash
swiftc -O -o <weread-help-dir>/bin/weread_flip_web \
  <skill-or-help>/scripts/weread_flip_web.swift
```

Launch on the Mac (background; do not block the agent for 30 minutes without a status poll plan):

```bash
export WEREAD_READER_URL="<reader-url>"
export WEREAD_BOOK_TITLE="<book-title>"
export WEREAD_BOOK_ID="<book-id>"
export WEREAD_HELP_DIR="<weread-help-dir>"
export WEREAD_DURATION_MIN="30"
export WEREAD_DWELL_MIN="15"
export WEREAD_DWELL_MAX="40"
nohup <binPath> >> "<weread-help-dir>/flip-web-stdout.txt" 2>&1 &
echo $! > "<weread-help-dir>/flip-web.pid"
```

Behavior baked into the script:

1. Focus / restore a `weread.qq.com/web/reader/` tab; if the active tab leaves the reader, restore immediately (do not treat a Twinkle/extension tab as login).
2. Dwell randomly 15–40s with light mouse move + scroll, then page-advance.
3. Before each page advance, run Chrome `execute javascript` on the active tab:
   - Click visible `下一章` / `下一回` → log `NEXT_CHAPTER` and skip that cycle's content click.
   - Book-end signals (`全书完` / `已经读完` / `本书已读完` / `再读一遍` / …) → click `再读一遍` / `从头开始` or first-chapter link, else navigate to `<reader-url>`; log `BOOK_RESTART`.
   - If Apple Events JS is disabled → log `JS_UNAVAILABLE` once and fall back to click+scroll.
4. End with `DONE_WEB` (or `STOPPED_NEED_LOGIN` on real login wall / exhausted restore).

Poll `<weread-help-dir>/flip-web-status.txt` and `flip-web.log`. See [references/ops.md](references/ops.md).

## After each session: effective-time check + one retry

1. Wait until status is terminal (`DONE_WEB` / `STOPPED_NEED_LOGIN`) or the process exits. A `DONE_WEB` status only means the timer elapsed; it does **not** prove WeRead credited reading time.
2. Query today's effective reading seconds through the installed official `weread-skills` workflow. Read its `readdata.md` first, use its current `skill_version`, and obey any returned upgrade instruction. Values are seconds. Example request shape (use only as specified by the official skill):

```bash
curl -sS -X POST "https://i.weread.qq.com/api/agent/gateway" \
  -H "Authorization: Bearer $WEREAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"api_name":"/readdata/detail","mode":"weekly","skill_version":"<weread-skills-version>"}'
```

3. In `readTimes`, find **today's** bucket (key = day-start unix timestamp in the user timezone). Value is **seconds**.
4. If today's seconds **< 1800** (30 minutes) **and** this was the first session of the run → start **exactly one** more ~30 minute flip session from current progress.
5. Cap at one retry. Never loop forever even if still under 1800s.
6. If the actual daily reading time is still far below the session wall-clock duration (especially only a few minutes), treat the session as **not successful**, even if the process says `DONE_WEB`. Inspect `flip-web.log`, `flip-web-stdout.txt`, current Chrome active-tab URL/title, and whether the reader advanced chapters; do not claim completion based on elapsed time or flip count.
7. A zero `nextChapter` / `bookRestarts` counter is not itself proof of failure, but if Chrome is at a chapter/book ending, explicitly activate the visible `下一章` / `下一回` control. At the whole-book ending, activate `再读一遍` / `从头开始` and verify that the title returns to an opening chapter before continuing. Do not leave the reader parked at the end.
8. If `STOPPED_NEED_LOGIN` occurs with an empty or non-reader tab string, classify it as **reader restore failure**, not confirmed logout. Check the logged-in Chrome reader tab before asking the user to log in. Only ask for QR/login if the reader itself visibly presents a login wall.

Follow `weread-skills` / `readdata.md` for field units and version reporting. Do not invent minute/hour units.

## Result reporting

Tell the calling agent/user:

- Session outcome token(s): `DONE_WEB` / `STOPPED_NEED_LOGIN` / whether a retry ran
- `flips`, `nextChapter` clicks, `bookRestarts` when present in the status line
- Approximate chapter/title from the final tab string, and whether chapter/end transitions were observed
- Today's effective reading: seconds and "x 小时 y 分钟" (from `/readdata/detail`, not wall-clock dwell)
- Whether a second session was triggered because today < 1800s
- Explicitly distinguish timer completion from successful credited reading; if the post-session stats do not meet target, report failure and diagnose before stopping

## Chrome JS permission

If logs show `JS_UNAVAILABLE`, chapter-end clicks will not work until the user enables:

**Google Chrome → View → Developer → Allow JavaScript from Apple Events**

Flip continues with click+scroll fallback either way.
