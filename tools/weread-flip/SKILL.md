---
name: weread-flip
description: Chrome 网页版微信读书慢速翻页刷有效时长；处理下一章/下一回、读完重头、结束后按当日有效时长不足 30 分钟补跑一轮。Use when the user wants WeRead web reading time, slow page flips in Chrome weread.qq.com, chapter transitions, or effective-time retry after a session.
---

# weread-flip

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

## Local config and external records

The machine-specific config lives only at:

```text
~/.agents/local-config/weread-flip/weread-flip.json
```

Schema:

```json
{
  "docs": { "root": "<absolute-obsidian-docs-root>" },
  "bookTitle": "<book-title>",
  "bookId": "<book-id>",
  "readerUrl": "<reader-url>",
  "durationMin": 30,
  "dwellMin": 15,
  "dwellMax": 40,
  "effectiveRetryThresholdSec": 1800
}
```

Derive the runtime directory as `<docs.root>/weread-flip`. Keep logs, status, compiled binary, and dated session records there. Keep Swift source in the installed skill and its source repository. Never use a Desktop fallback or create a second local config. `docs.root` is the user’s external Obsidian documentation root; the `weread-flip` subdirectory is defined by this skill.

## Prerequisites

1. At startup, verify `~/.agents/skills/weread-skills/SKILL.md` exists and has a valid `name: weread-skills` frontmatter. If missing, install the official Tencent skill before any WeRead API or reading-stat operation, using the skills-loop installer with source `Tencent/WeChatReading`, path `skills`, name `weread-skills`. Never copy or recreate the official skill manually; never modify its files. If installation fails, stop API-dependent work and tell the user.
2. Read the relevant official `weread-skills` docs before API use. Follow its current version and upgrade instructions (including any `upgrade_info`) before continuing. Reading stats must be queried through this official skill/API workflow, not guessed or replaced by local timers.
3. Target a macOS machine with Google Chrome and Accessibility / Automation permissions for the controlling agent.
4. User is logged into weread.qq.com in Chrome (reader opens without QR).
5. Compiled flip binary, or `swiftc` available to build `scripts/weread_flip_web.swift`.
6. For effective-time checks: `WEREAD_API_KEY` in the environment; never print or persist it.

## Build / launch the flip binary

Derive `<runtime-dir>` from `docs.root/weread-flip`. Prefer `<runtime-dir>/bin/weread_flip_web`; otherwise compile:

```bash
mkdir -p "<runtime-dir>/bin"
swiftc -O -o "<runtime-dir>/bin/weread_flip_web" \
  "<skill-dir>/scripts/weread_flip_web.swift"
```

Read book and timing values from the local config, then pass them explicitly:

```bash
export WEREAD_READER_URL="<reader-url>"
export WEREAD_BOOK_TITLE="<book-title>"
export WEREAD_BOOK_ID="<book-id>"
export WEREAD_HELP_DIR="<runtime-dir>"
export WEREAD_DURATION_MIN="30"
export WEREAD_DWELL_MIN="15"
export WEREAD_DWELL_MAX="40"
nohup "<runtime-dir>/bin/weread_flip_web" >> "<runtime-dir>/flip-web-stdout.txt" 2>&1 &
echo $! > "<runtime-dir>/flip-web.pid"
```

Behavior baked into the script:

1. Focus / restore a `weread.qq.com/web/reader/` tab; if the active tab leaves the reader, restore immediately (do not treat a Twinkle/extension tab as login).
2. Dwell randomly 15–40s with light mouse move + scroll, then page-advance.
3. Before each page advance, run Chrome `execute javascript` on the active tab:
   - Click visible `下一章` / `下一回` → log `NEXT_CHAPTER` and skip that cycle's content click.
   - Book-end signals (`全书完` / `已经读完` / `本书已读完` / `再读一遍` / …) → click `再读一遍` / `从头开始` or first-chapter link, else navigate to `<reader-url>`; log `BOOK_RESTART`.
   - If Apple Events JS is disabled → log `JS_UNAVAILABLE` once and fall back to click+scroll.
4. End with `DONE_WEB` (or `STOPPED_NEED_LOGIN` on real login wall / exhausted restore).

Poll `<runtime-dir>/flip-web-status.txt` and `flip-web.log`. See [references/ops.md](references/ops.md).

## After each session: effective-time check + one retry

1. Wait until status is terminal (`DONE_WEB` / `STOPPED_NEED_LOGIN`) or the process exits. `DONE_WEB` means the timer elapsed; it does **not** prove WeRead credited reading time.
2. Query today's effective reading seconds through the installed official `weread-skills` workflow. Read its `readdata.md` first, use its current `skill_version`, and obey any returned upgrade instruction. Values are seconds. Example request shape (use only as specified by the official skill):

```bash
curl -sS -X POST "https://i.weread.qq.com/api/agent/gateway" \
  -H "Authorization: Bearer $WEREAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"api_name":"/readdata/detail","mode":"weekly","skill_version":"<weread-skills-version>"}'
```

3. In `readTimes`, find **today's** bucket (key = day-start unix timestamp in the user timezone). Value is **seconds**.
4. If today's seconds are below `effectiveRetryThresholdSec` (default 1800) and this was the first session of the run, start **exactly one** more ~30 minute flip session from current progress.
5. Cap at one retry. Never loop forever even if still under the threshold.
6. If actual daily reading time is far below session wall-clock duration (especially only a few minutes), treat the session as **not successful**, even if the process says `DONE_WEB`. Inspect the run log, stdout, current Chrome active-tab URL/title, and whether the reader advanced chapters; do not claim completion based on elapsed time or flip count.
7. A zero `nextChapter` / `bookRestarts` counter is not itself proof of failure, but if Chrome is at a chapter/book ending, explicitly activate the visible `下一章` / `下一回` control. At the whole-book ending, activate `再读一遍` / `从头开始` and verify that the title returns to an opening chapter before continuing. Do not leave the reader parked at the end.
8. If `STOPPED_NEED_LOGIN` occurs with an empty or non-reader tab string, classify it as reader restore failure, not confirmed logout. Check the logged-in Chrome reader tab before asking the user to log in. Only ask for QR/login if the reader itself visibly presents a login wall.

Follow `weread-skills` / `readdata.md` for field units and version reporting. Do not invent minute/hour units.

## Result reporting and history

Append a record to `<runtime-dir>/history/YYYY-MM-DD.md` after each completed run, including session tokens, flips/transitions, final reader title, official effective seconds, whether retry ran, and a diagnosis when timer and credited time diverge. Never record API keys, cookies, or tokens. Preserve append-only run logs and history across sessions; keep the binary and transient status files alongside them under `<runtime-dir>`.

Tell the calling agent/user:

- Session outcome token(s): `DONE_WEB` / `STOPPED_NEED_LOGIN` / whether a retry ran
- `flips`, `nextChapter` clicks, `bookRestarts` when present in the status line
- Approximate chapter/title from the final tab string, and whether chapter/end transitions were observed
- Today's effective reading: seconds and "x 小时 y 分钟" (from `/readdata/detail`, not wall-clock dwell)
- Whether a second session was triggered because today was below threshold
- Explicitly distinguish timer completion from successful credited reading; if post-session stats remain below threshold, report failure and diagnosis

## Chrome JS permission

If logs show `JS_UNAVAILABLE`, chapter-end clicks will not work until the user enables:

**Google Chrome → View → Developer → Allow JavaScript from Apple Events**

Flip continues with click+scroll fallback either way.

## AppleScript runtime

- `runOSA` must close parent pipe write ends and drain stdout and stderr on two threads before `waitUntilExit`. Leaving a write end open makes `readDataToEndOfFile` block forever after `osascript` exits, so the log stays at `START_WEB` and never reaches `READER_OK`.
- Do not read window bounds from System Events. `osascript` has no assistive access here, so that call returns `NO_BOUNDS` and the loop never flips. Use Chrome `bounds of front window` (`left, top, right, bottom`) and convert to `x, y, width, height`.
