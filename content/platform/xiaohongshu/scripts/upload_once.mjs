// Same-Tab chooser primitive. Call from the documented browser REPL, not a shell browser.
// A receipt is file selection only; the caller must read platform media state.
export async function uploadOnce({ tab, trigger, assetPath, priorState, chooserTimeoutMs = 10000 }) {
  if (priorState !== "empty") {
    return { outcome: "read_only_required", reasonCode: "existing_or_uncertain_side_effect", selectionAttempted: false };
  }
  if (typeof assetPath !== "string" || !(/^(\/|[A-Za-z]:[\\/])/.test(assetPath))) {
    throw new TypeError("assetPath must be an existing verified absolute path");
  }
  let pending;
  try {
    pending = tab.playwright.waitForEvent("filechooser", { timeoutMs: chooserTimeoutMs })
      .then(chooser => ({ chooser }), error => ({ error: String(error) }));
  } catch (error) {
    return { outcome: "blocked", reasonCode: "filechooser_api_unavailable", selectionAttempted: false, error: String(error) };
  }
  let triggerError;
  try { await trigger.click({ timeoutMs: 6000 }); }
  catch (error) { triggerError = String(error); }
  const event = await pending;
  const evidence = { chooserObserved: !!event.chooser, selectionAttempted: false };
  if (triggerError || event.error) {
    return { ...evidence, outcome: "observe_before_recovery", reasonCode: triggerError ? "upload_trigger_failed" : "filechooser_not_opened", error: triggerError || event.error };
  }
  try {
    await event.chooser.setFiles([assetPath], { timeoutMs: 10000 });
    return { ...evidence, selectionAttempted: true, selectionReceipt: true, outcome: "verify_platform_media", reasonCode: "files_selected" };
  } catch (error) {
    return { ...evidence, selectionAttempted: true, selectionReceipt: false, outcome: "read_only_required", reasonCode: "file_selection_unconfirmed", error: String(error) };
  }
}
