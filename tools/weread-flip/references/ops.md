# weread-flip ops

## Status / log files

Under `<runtime-dir> = <docs.root>/weread-flip` (where `docs.root` comes from `~/.agents/local-config/weread-flip/weread-flip.json` and points to the user's Obsidian docs root):

| File | Role |
|------|------|
| `flip-web-status.txt` | Latest status line (overwrite) |
| `flip-web.log` | Append-only session log |
| `flip-web-out.txt` | Per-run captured lines |
| `flip-web.pid` | Background PID |
| `flip-web-stdout.txt` | Optional nohup stdout/stderr |
| `bin/weread_flip_web` | Compiled binary |
| `history/YYYY-MM-DD.md` | Human-readable session and effective-time record |

Swift source stays under the installed skill/source repository; do not copy it into the Obsidian runtime directory.

## Status tokens

| Token | Meaning |
|-------|---------|
| `START_WEB` | Session started |
| `READER_OK` | Active tab is a weread reader URL |
| `LOST_READER` / `LOST_READER_MID` | Active tab left reader; restore attempted |
| `RESTORED_READER` | Reader tab focused again |
| `RESTORE_RETRY` | Restore failed; will retry (not yet login stop) |
| `NEXT_CHAPTER` | JS clicked 下一章/下一回 |
| `BOOK_RESTART` | Book finished; restarted from beginning / 再读一遍 |
| `JS_UNAVAILABLE` | Chrome Apple Events JS disabled or failed; click+scroll fallback |
| `DONE_WEB` | Duration completed normally |
| `STOPPED_NEED_LOGIN` | Login wall, or restore exhausted — stop and ask user; do not empty-loop |

## Effective-time retry

1. After terminal status, call `/readdata/detail` with `mode=weekly` (or `monthly` if you need today's bucket there).
2. `readTimes` values are **seconds**.
3. If today's bucket `< 1800` and no retry yet → one more session.
4. Report flips + today effective minutes after the final session.

## Safety

- Do not treat `chrome-extension://…` or local `http://127.0.0.1/…` tabs as proof of logout; restore the reader tab instead.
- Only prompt for QR when the reader cannot be restored or the tab clearly shows login.
