import assert from "node:assert/strict";
import { uploadOnce } from "./upload_once.mjs";

const assetPath = "/verified/canonical-cover.png";
let passed = 0;
function fixture({ chooserFails = false, triggerFails = false, selectionFails = false, apiFails = false } = {}) {
  const calls = [];
  const chooser = { async setFiles(files) {
    calls.push("setFiles");
    assert.deepEqual(files, [assetPath]);
    if (selectionFails) throw new Error("selection interrupted");
  } };
  const tab = { playwright: { waitForEvent(event) {
    calls.push("wait");
    assert.equal(event, "filechooser");
    if (apiFails) throw new Error("unsupported");
    return chooserFails ? Promise.reject(new Error("chooser timeout")) : Promise.resolve(chooser);
  } } };
  const trigger = { async click() {
    calls.push("click");
    await Promise.resolve(); // Already-rejected wait must be handled during the trigger.
    if (triggerFails) throw new Error("trigger timeout");
  } };
  return { tab, trigger, calls, priorState: "empty" };
}

let f = fixture();
let result = await uploadOnce({ ...f, assetPath });
assert.deepEqual(f.calls, ["wait", "click", "setFiles"]);
assert.equal(result.outcome, "verify_platform_media"); // Not platform upload success.
assert.equal(result.selectionReceipt, true);
passed++;

f = fixture({ chooserFails: true });
result = await uploadOnce({ ...f, assetPath });
assert.deepEqual(f.calls, ["wait", "click"]);
assert.equal(result.reasonCode, "filechooser_not_opened");
assert.equal(result.selectionAttempted, false);
passed++;

f = fixture({ triggerFails: true });
result = await uploadOnce({ ...f, assetPath });
assert.deepEqual(f.calls, ["wait", "click"]);
assert.equal(result.chooserObserved, true);
assert.equal(result.reasonCode, "upload_trigger_failed");
passed++;

f = fixture({ selectionFails: true });
result = await uploadOnce({ ...f, assetPath });
assert.deepEqual(f.calls, ["wait", "click", "setFiles"]);
assert.equal(result.selectionAttempted, true);
assert.equal(result.outcome, "read_only_required");
passed++;

f = fixture({ apiFails: true });
result = await uploadOnce({ ...f, assetPath });
assert.deepEqual(f.calls, ["wait"]);
assert.equal(result.reasonCode, "filechooser_api_unavailable");
passed++;

for (const priorState of [undefined, "uploaded", "processing", "upload_intent", "published_pending_review", "publish_unconfirmed", "uncertain"]) {
  f = fixture();
  result = await uploadOnce({ ...f, assetPath, priorState });
  assert.deepEqual(f.calls, []);
  assert.equal(result.outcome, "read_only_required");
  passed++;
}
f = fixture();
await assert.rejects(uploadOnce({ ...f, assetPath: "relative.png" }), TypeError);
assert.deepEqual(f.calls, []);
passed++;
console.log(`PASS ${passed} offline upload invariants; no live browser writes`);
