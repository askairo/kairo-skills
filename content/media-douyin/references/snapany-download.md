# SnapAny download recovery

Use this reference only after the source URL, creator authorization, and candidate deduplication have passed. It describes visible UI behavior; do not hardcode signed URLs, proxy hosts, browser profile paths, or local account details.

## Procedure

1. Open `https://snapany.com/zh`, paste the verified source URL, and click the visible `提取视频图片` action. Wait for the result card instead of assuming a fixed delay or reusing an old result.
2. In the result card, identify the top `下载视频` action. Confirm the adjacent down-arrow/`More options` control belongs to that card; do not click an audio-only or lower-resolution card by position alone.
3. Attempt the visible normal `下载视频` action first. Wait up to 180 seconds and inspect the controlled temporary/download directory. A new tab, a media preview, or a `.crdownload` file alone is not proof that a local file was downloaded.
4. If the normal action fails or only opens a media page, refresh the SnapAny page, paste the same source URL, click `提取视频图片`, and wait for a fresh result card. Then click the card's arrow and choose the visible menu item `备用下载地址` or a visible alternate format. Do not open, copy, or infer the signed media URL directly.
5. If the backup action fails, opens another result page, or leaves only a temporary file, refresh and re-parse again before the next attempt. Alternate normal and visible backup methods for up to four effective attempts, with at least two normal/backup cycles and a 180-second wait per attempt. Record each attempt and stop only when a complete file is validated or all four attempts and visible methods fail.
6. After any backup action opens another result page, wait for it to load, locate the same video card, open its arrow again, and wait for a browser download event while activating the visible `备用下载地址` menu item. A new tab or a media preview is not proof that a local file was downloaded.
5. Save into a run-scoped temporary directory and record the candidate ID, source URL, selected method, and local filename in the run record. Never use an arbitrary old file from Downloads as the candidate.

## Acceptance and fallback

- Accept the file only after checking that it is complete and playable, has a video track and (for music content) an audio track, has a plausible duration, and the preview is not black, frozen, or silent. The browser preview should report a loaded/ready media state; a successful download event alone is insufficient.
- If the selected backup address fails, try only the next clearly visible backup address or format offered for the same card. Do not scrape or invent alternate signed URLs, and do not repeatedly retry a failing address.
- If every visible option fails, record the exact failure, leave the sequential cursor unchanged, and continue only according to the run-level limit. Do not mark the candidate published.
- Delete the run-scoped file only after the platform publication has a confirmed success or review status and the state record has been written. If publication is uncertain, keep the file until the result is resolved or the run's retention policy handles it.
