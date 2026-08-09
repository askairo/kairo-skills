# SnapAny download recovery

Use this reference only after the source URL, creator authorization, and candidate deduplication have passed. It describes visible UI behavior; do not hardcode signed URLs, proxy hosts, browser profile paths, or local account details.

## Procedure

1. Open `https://snapany.com/zh`, paste the verified source URL, and click the visible `提取视频图片` action. Wait for the result card instead of assuming a fixed delay or reusing an old result.
2. In the result card, identify the top `下载视频` action. Confirm the adjacent down-arrow/`More options` control belongs to that card; do not click an audio-only or lower-resolution card by position alone.
3. Before any download action, record a run-scoped baseline of the controlled temporary/download directory. Attempt the visible normal `下载视频` action first. Wait up to 180 seconds and inspect the directory. A new tab, a media preview, or a `.crdownload` file alone is not proof that a local file was downloaded.
4. If the normal action fails or only opens a media page, refresh the SnapAny page, paste the same source URL, click `提取视频图片`, and wait for a fresh result card. Then click the card's arrow and choose the visible menu item `备用下载地址` or a visible alternate format. Do not open, copy, or infer the signed media URL directly.
5. If the backup action fails, opens another result page, or leaves only a temporary file, refresh and re-parse again before the next attempt. Alternate normal and visible backup methods for up to four effective attempts, with at least two normal/backup cycles and a 180-second wait per attempt. Record each attempt and stop only when a complete file is validated or all four attempts and visible methods fail.
6. After any backup action opens another result page, wait for it to load, locate the same video card, open its arrow again, and activate the visible `备用下载地址` menu item. A new tab or a media preview is not proof that a local file was downloaded.
7. Treat a missing or timed-out browser download event as an observation, not an automatic failure. Compare the post-action directory against the pre-action baseline; only a uniquely attributable new file created during this run may continue to validation. Never adopt a pre-existing file merely because its name looks plausible.
8. Save the validated file into the configured resource directory with a stable candidate-based filename, and record the candidate ID, source URL, selected visible methods, local filename, size and content hash. Never use an arbitrary old file from Downloads as the candidate.

## Acceptance and fallback

- Accept the file only after checking that it is complete and playable, has a video track and (for music content) an audio track, has a plausible duration, and the preview is not black, frozen, or silent. Prefer a media probe; if it is unavailable, use the operating system's media metadata plus a successful thumbnail/preview decode and record that fallback. A successful download event alone is insufficient, and a missing event does not invalidate a file that has a unique fresh-download trail and passes these checks.
- If the selected backup address fails, try only the next clearly visible backup address or format offered for the same card. Do not scrape or invent alternate signed URLs, and do not repeatedly retry a failing address.
- If every visible option fails, record the exact failure, leave the sequential cursor unchanged, and continue only according to the run-level limit. Do not mark the candidate published.
- Delete the run-scoped file only after the platform publication has a confirmed success or review status and the state record has been written. If publication is uncertain, keep the file until the result is resolved or the run's retention policy handles it.
