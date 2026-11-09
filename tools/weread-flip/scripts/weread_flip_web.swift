import Cocoa
import Foundation

// Machine- and book-specific values must come from the caller's local config.
guard let readerURL = ProcessInfo.processInfo.environment["WEREAD_READER_URL"],
      let bookTitle = ProcessInfo.processInfo.environment["WEREAD_BOOK_TITLE"],
      let bookId = ProcessInfo.processInfo.environment["WEREAD_BOOK_ID"],
      let helpDir = ProcessInfo.processInfo.environment["WEREAD_HELP_DIR"],
      !readerURL.isEmpty, !bookTitle.isEmpty, !bookId.isEmpty, !helpDir.isEmpty else {
  fputs("Missing required WEREAD_READER_URL, WEREAD_BOOK_TITLE, WEREAD_BOOK_ID, or WEREAD_HELP_DIR environment value.\n", stderr)
  exit(2)
}
let durationMinutes = Double(ProcessInfo.processInfo.environment["WEREAD_DURATION_MIN"] ?? "30") ?? 30.0
let dwellMin = Double(ProcessInfo.processInfo.environment["WEREAD_DWELL_MIN"] ?? "15") ?? 15.0
let dwellMax = Double(ProcessInfo.processInfo.environment["WEREAD_DWELL_MAX"] ?? "40") ?? 40.0

func runOSA(_ source: String, capture: Bool = true) -> (Int32, String) {
  let p = Process()
  p.executableURL = URL(fileURLWithPath: "/usr/bin/osascript")
  p.arguments = ["-e", source]
  let out = Pipe()
  let err = Pipe()
  p.standardOutput = out
  p.standardError = err
  do { try p.run() } catch { return (1, "") }
  // Parent must drop its write ends. Otherwise read-to-EOF blocks forever
  // after the child exits, and a full stderr pipe deadlocks waitUntilExit.
  try? out.fileHandleForWriting.close()
  try? err.fileHandleForWriting.close()
  let group = DispatchGroup()
  var outData = Data()
  group.enter()
  DispatchQueue.global(qos: .userInitiated).async {
    outData = out.fileHandleForReading.readDataToEndOfFile()
    group.leave()
  }
  group.enter()
  DispatchQueue.global(qos: .userInitiated).async {
    _ = err.fileHandleForReading.readDataToEndOfFile()
    group.leave()
  }
  group.wait()
  p.waitUntilExit()
  let s = capture
    ? (String(data: outData, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? "")
    : ""
  return (p.terminationStatus, s)
}

func activateChrome() {
  _ = runOSA("tell application \"Google Chrome\" to activate", capture: false)
}

func frontIsChrome() -> Bool {
  let (_, s) = runOSA("tell application \"System Events\" to get name of first process whose frontmost is true")
  return s == "Google Chrome"
}

func chromeTabInfo() -> String {
  let (_, s) = runOSA("""
  tell application "Google Chrome"
    if (count of windows) = 0 then return "NO_WINDOW"
    set t to active tab of front window
    return (URL of t) & " | " & (title of t)
  end tell
  """)
  return s
}

func isReaderURL(_ info: String) -> Bool {
  return info.contains("weread.qq.com/web/reader/")
}

func isLoginWall(_ info: String) -> Bool {
  let lower = info.lowercased()
  if info.contains("登录") || lower.contains("login") || info.contains("扫码") {
    // login page without reader content
    if !isReaderURL(info) { return true }
    if isReaderURL(info) && !info.contains(bookTitle) && info.contains("登录") { return true }
  }
  return false
}

/// Aggressively restore/focus the weread reader tab. Returns true if active tab is a reader URL.
func ensureReaderTab(retries: Int = 3) -> Bool {
  for attempt in 1...retries {
    activateChrome()
    let script = """
    tell application "Google Chrome"
      activate
      set targetURL to "\(readerURL)"
      set foundWin to 0
      set foundTab to 0
      repeat with w from 1 to (count of windows)
        repeat with t from 1 to (count of tabs of window w)
          set u to URL of tab t of window w
          if u contains "weread.qq.com/web/reader/" then
            set foundWin to w
            set foundTab to t
            exit repeat
          end if
        end repeat
        if foundWin is not 0 then exit repeat
      end repeat
      if foundWin is not 0 then
        set index of window foundWin to 1
        set active tab index of window foundWin to foundTab
        return "FOCUSED"
      end if
      -- no reader tab: prefer navigating an existing weread tab
      set foundWin to 0
      set foundTab to 0
      repeat with w from 1 to (count of windows)
        repeat with t from 1 to (count of tabs of window w)
          set u to URL of tab t of window w
          if u contains "weread.qq.com" then
            set foundWin to w
            set foundTab to t
            exit repeat
          end if
        end repeat
        if foundWin is not 0 then exit repeat
      end repeat
      if foundWin is not 0 then
        set index of window foundWin to 1
        set active tab index of window foundWin to foundTab
        set URL of tab foundTab of window foundWin to targetURL
        return "NAVIGATED"
      end if
      -- open new tab on front window, or new window
      if (count of windows) = 0 then
        make new window
        set URL of active tab of front window to targetURL
      else
        tell front window
          set newTab to make new tab with properties {URL:targetURL}
          set active tab index to (index of newTab)
        end tell
        set index of front window to 1
      end if
      return "OPENED"
    end tell
    """
    let (st, result) = runOSA(script)
    Thread.sleep(forTimeInterval: attempt == 1 ? 2.0 : 2.5)
    let info = chromeTabInfo()
    if isReaderURL(info) {
      return true
    }
    // If AppleScript failed or tab still wrong, try once more with open location
    if attempt == retries || st != 0 || result.isEmpty {
      _ = runOSA("tell application \"Google Chrome\" to open location \"\(readerURL)\"", capture: false)
      Thread.sleep(forTimeInterval: 2.5)
      if isReaderURL(chromeTabInfo()) { return true }
    }
  }
  return isReaderURL(chromeTabInfo())
}

func click(_ x: Double, _ y: Double) {
  let sx = Int(x.rounded())
  let sy = Int(y.rounded())
  let (st, _) = runOSA("""
  tell application "System Events"
    set frontmost of process "Google Chrome" to true
    delay 0.05
    click at {\(sx), \(sy)}
  end tell
  """, capture: false)
  if st != 0 {
    let pt = CGPoint(x: x + Double.random(in: -1.5...1.5), y: y + Double.random(in: -1.5...1.5))
    if let m = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: pt, mouseButton: .left) { m.post(tap: .cghidEventTap) }
    Thread.sleep(forTimeInterval: 0.05)
    if let e = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: pt, mouseButton: .left) { e.post(tap: .cghidEventTap) }
    Thread.sleep(forTimeInterval: 0.04)
    if let e = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: pt, mouseButton: .left) { e.post(tap: .cghidEventTap) }
  }
}

func move(_ x: Double, _ y: Double) {
  let pt = CGPoint(x: x, y: y)
  if let m = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: pt, mouseButton: .left) {
    m.post(tap: .cghidEventTap)
  }
}

func scrollAt(_ x: Double, _ y: Double, _ dy: Int32) {
  let pt = CGPoint(x: x, y: y)
  if let m = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: pt, mouseButton: .left) {
    m.post(tap: .cghidEventTap)
  }
  Thread.sleep(forTimeInterval: 0.03)
  if let e = CGEvent(scrollWheelEvent2Source: nil, units: .pixel, wheelCount: 1, wheel1: dy, wheel2: 0, wheel3: 0) {
    e.post(tap: .cghidEventTap)
  }
}

func bounds() -> (Double, Double, Double, Double)? {
  // Chrome's own bounds are left,top,right,bottom and do not need Accessibility.
  // System Events position/size is blocked while osascript lacks assistive access.
  let (_, s) = runOSA("""
  tell application "Google Chrome"
    if (count of windows) = 0 then return ""
    set b to bounds of front window
    set x to item 1 of b
    set y to item 2 of b
    set w to (item 3 of b) - x
    set h to (item 4 of b) - y
    return (x as text)&","&(y as text)&","&(w as text)&","&(h as text)
  end tell
  """)
  let parts = s.split(separator: ",").compactMap { Double($0.trimmingCharacters(in: .whitespaces)) }
  guard parts.count == 4, parts[2] > 50, parts[3] > 50 else { return nil }
  return (parts[0], parts[1], parts[2], parts[3])
}

/// Chrome JS via Apple Events. Returns action token or JS_UNAVAILABLE / JS_ERROR / NONE.
var jsUnavailableLogged = false
func executeReaderJS() -> String {
  // Keep JS compact; escape for AppleScript double-quoted string carefully via hex-ish approach:
  // We pass JS through osascript argv-free by embedding; replace " carefully.
  let js = #"""
  (function(){
    function vis(el){
      if(!el) return false;
      var r=el.getBoundingClientRect();
      if(r.width<2||r.height<2) return false;
      var s=window.getComputedStyle(el);
      return s.visibility!=='hidden'&&s.display!=='none'&&Number(s.opacity)!==0;
    }
    function txt(el){return ((el.innerText||el.textContent||'')+'').replace(/\s+/g,' ').trim();}
    var body=(document.body&&(document.body.innerText||''))||'';
    var endMarks=['全书完','已经读完','本书已读完','读完了','恭喜你读完','全书完结'];
    var ended=false;
    for(var i=0;i<endMarks.length;i++){ if(body.indexOf(endMarks[i])>=0){ ended=true; break; } }
    var nodes=document.querySelectorAll('a,button,div,span,li,p,section');
    function findClick(cands){
      for(var i=0;i<nodes.length;i++){
        var el=nodes[i];
        if(!vis(el)) continue;
        var t=txt(el);
        if(!t||t.length>40) continue;
        for(var j=0;j<cands.length;j++){
          if(t===cands[j]||t.indexOf(cands[j])>=0) return el;
        }
      }
      return null;
    }
    var restart=findClick(['再读一遍','从头开始','重新阅读']);
    if(ended||restart){
      if(restart){ restart.click(); return 'BOOK_RESTART'; }
      var links=document.querySelectorAll('a');
      for(var i=0;i<links.length;i++){
        var a=links[i]; if(!vis(a)) continue;
        var t=txt(a);
        if(/第\s*一\s*[章回]|开篇|楔子|第一回/.test(t)){ a.click(); return 'BOOK_RESTART'; }
      }
      var cat=document.querySelector('.readerCatalog a, .catalog_list a, [class*="catalog"] a, [class*="chapterList"] a');
      if(cat){ cat.click(); return 'BOOK_RESTART'; }
      return 'BOOK_END';
    }
    var next=findClick(['下一章','下一回']);
    if(next){ next.click(); return 'NEXT_CHAPTER'; }
    return 'NONE';
  })()
  """#
  // Escape for AppleScript: backslash and double-quote
  let escaped = js
    .replacingOccurrences(of: "\\", with: "\\\\")
    .replacingOccurrences(of: "\"", with: "\\\"")
  let (_, raw) = runOSA("""
  tell application "Google Chrome"
    if (count of windows) = 0 then return "NO_WINDOW"
    try
      set r to execute active tab of front window javascript "\(escaped)"
      return r as text
    on error errMsg
      return "JS_ERROR:" & errMsg
    end try
  end tell
  """)
  if raw.hasPrefix("JS_ERROR:") || raw == "NO_WINDOW" {
    // Any AppleScript JS failure: treat as unavailable and fall back (do not crash)
    return "JS_UNAVAILABLE"
  }
  if raw.isEmpty { return "NONE" }
  return raw
}

try? FileManager.default.createDirectory(atPath: helpDir, withIntermediateDirectories: true)
let logPath = helpDir + "/flip-web.log"
let statusPath = helpDir + "/flip-web-status.txt"
let outPath = helpDir + "/flip-web-out.txt"
let pidPath = helpDir + "/flip-web.pid"

func log(_ msg: String) {
  let df = DateFormatter(); df.locale = Locale(identifier: "en_US_POSIX")
  df.dateFormat = "yyyy-MM-dd HH:mm:ss Z"
  let line = "\(df.string(from: Date())) \(msg)\n"
  if let data = line.data(using: .utf8) {
    if FileManager.default.fileExists(atPath: logPath), let fh = FileHandle(forWritingAtPath: logPath) {
      fh.seekToEndOfFile(); fh.write(data); try? fh.close()
    } else {
      FileManager.default.createFile(atPath: logPath, contents: data)
    }
    if let fh2 = FileHandle(forWritingAtPath: outPath) {
      fh2.seekToEndOfFile(); fh2.write(data); try? fh2.close()
    } else {
      FileManager.default.createFile(atPath: outPath, contents: data)
    }
  }
  try? "\(msg)\n".write(toFile: statusPath, atomically: true, encoding: .utf8)
  print(msg); fflush(stdout)
}

try? "\(getpid())\n".write(toFile: pidPath, atomically: true, encoding: .utf8)

let start = Date()
let duration: TimeInterval = durationMinutes * 60
var flips = 0
var nextChapterClicks = 0
var bookRestarts = 0
var lostRestoreFails = 0
let maxRestoreFails = 8

FileManager.default.createFile(atPath: outPath, contents: Data())
log("START_WEB book=\(bookTitle) bookId=\(bookId) dwell=\(Int(dwellMin))-\(Int(dwellMax))s input=click+scroll+js duration=\(Int(durationMinutes))m chrome=weread.qq.com")

activateChrome()
Thread.sleep(forTimeInterval: 0.5)
if !ensureReaderTab(retries: 4) {
  let tab = chromeTabInfo()
  if isLoginWall(tab) {
    log("STOPPED_NEED_LOGIN tab=\(tab)")
  } else {
    log("STOPPED_NEED_LOGIN tab=\(tab)")  // keep legacy token for routines; reason may be restore failure
  }
  exit(2)
}
let tab0 = chromeTabInfo()
log("READER_OK tab=\(tab0)")
if isLoginWall(tab0) {
  log("STOPPED_NEED_LOGIN tab=\(tab0)")
  exit(2)
}

for _ in 0..<2 {
  _ = runOSA("tell application \"System Events\" to key code 53", capture: false)
  Thread.sleep(forTimeInterval: 0.15)
}

var advanceCounter = 0

while Date().timeIntervalSince(start) < duration {
  if !frontIsChrome() {
    log("REFOCUS_CHROME")
    activateChrome()
    Thread.sleep(forTimeInterval: 0.4)
  }

  let info = chromeTabInfo()
  if !isReaderURL(info) {
    log("LOST_READER tab=\(info); restoring")
    if isLoginWall(info) {
      // still try restore first — login may be another tab
    }
    if ensureReaderTab(retries: 3) {
      lostRestoreFails = 0
      log("RESTORED_READER tab=\(chromeTabInfo())")
    } else {
      lostRestoreFails += 1
      let after = chromeTabInfo()
      if isLoginWall(after) {
        log("STOPPED_NEED_LOGIN tab=\(after)")
        exit(2)
      }
      if lostRestoreFails >= maxRestoreFails {
        log("STOPPED_NEED_LOGIN tab=\(after)")  // exhausted restore; same token for callers
        exit(2)
      }
      log("RESTORE_RETRY fails=\(lostRestoreFails) tab=\(after)")
      Thread.sleep(forTimeInterval: 2.0)
      continue
    }
  } else {
    lostRestoreFails = 0
  }

  guard let b = bounds() else {
    log("NO_BOUNDS"); Thread.sleep(forTimeInterval: 5); continue
  }

  let lo = min(dwellMin, dwellMax)
  let hi = max(dwellMin, dwellMax)
  let dwell = Double.random(in: lo...hi)
  let dwellStart = Date()
  log("dwell_sec=\(Int(dwell)) flips=\(flips) elapsed=\(Int(Date().timeIntervalSince(start)))")

  while Date().timeIntervalSince(dwellStart) < dwell {
    let mx = b.0 + b.2 * Double.random(in: 0.28...0.68)
    let my = b.1 + b.3 * Double.random(in: 0.32...0.78)
    move(mx, my)
    if Double.random(in: 0...1) < 0.55 {
      let dy: Int32 = Int32.random(in: -90...(-20))
      scrollAt(mx, my, dy)
    }
    Thread.sleep(forTimeInterval: Double.random(in: 2.2...5.0))
    if Date().timeIntervalSince(start) >= duration { break }
    // Mid-dwell tab lock
    let mid = chromeTabInfo()
    if !isReaderURL(mid) {
      log("LOST_READER_MID tab=\(mid); restoring")
      _ = ensureReaderTab(retries: 2)
      break
    }
  }
  if Date().timeIntervalSince(start) >= duration { break }

  // Chapter / book-end handling via JS every advance (and after first)
  advanceCounter += 1
  var skippedPageClick = false
  if advanceCounter == 1 || advanceCounter % 1 == 0 {
    let action = executeReaderJS()
    if action == "JS_UNAVAILABLE" {
      if !jsUnavailableLogged {
        jsUnavailableLogged = true
        log("JS_UNAVAILABLE fallback=click+scroll (enable Chrome: View>Developer>Allow JavaScript from Apple Events)")
      }
    } else if action == "NEXT_CHAPTER" {
      nextChapterClicks += 1
      flips += 1
      skippedPageClick = true
      log("NEXT_CHAPTER flips=\(flips) nextChapterClicks=\(nextChapterClicks)")
      Thread.sleep(forTimeInterval: Double.random(in: 1.2...2.5))
    } else if action == "BOOK_RESTART" || action == "BOOK_END" {
      if action == "BOOK_END" {
        // Fallback: navigate to reader base URL (resume often starts ch1 after finish UX)
        _ = runOSA("""
        tell application "Google Chrome"
          if (count of windows) > 0 then set URL of active tab of front window to "\(readerURL)"
        end tell
        """, capture: false)
        Thread.sleep(forTimeInterval: 3.0)
        _ = executeReaderJS()
      }
      bookRestarts += 1
      flips += 1
      skippedPageClick = true
      log("BOOK_RESTART flips=\(flips) bookRestarts=\(bookRestarts) via=\(action)")
      Thread.sleep(forTimeInterval: Double.random(in: 2.0...3.5))
    }
  }

  if !skippedPageClick {
    let cx = b.0 + b.2 * Double.random(in: 0.55...0.72)
    let cy = b.1 + b.3 * Double.random(in: 0.40...0.70)
    click(cx, cy)
    Thread.sleep(forTimeInterval: 0.2)
    let sx = b.0 + b.2 * Double.random(in: 0.35...0.65)
    let sy = b.1 + b.3 * Double.random(in: 0.40...0.70)
    scrollAt(sx, sy, Int32.random(in: -220...(-80)))
    flips += 1
    Thread.sleep(forTimeInterval: Double.random(in: 0.8...1.8))
  }
}

let finalTab = chromeTabInfo()
log("DONE_WEB flips=\(flips) nextChapter=\(nextChapterClicks) restarts=\(bookRestarts) elapsed_sec=\(Int(Date().timeIntervalSince(start))) tab=\(finalTab)")
try? "DONE_WEB flips=\(flips) nextChapter=\(nextChapterClicks) restarts=\(bookRestarts) elapsed_sec=\(Int(Date().timeIntervalSince(start)))\n".write(toFile: statusPath, atomically: true, encoding: .utf8)
