# 抖音：同一 Chrome extension Tab 上传与预览恢复

沿用配置通道、已核验账号、`contentId + targetId` 锁、canonical 媒体及顺序游标。此流程不发现来源、不下载素材、不切换浏览器通道。

## 能力预检：完整文档优先

通过 `cua.getState()` 选择配置匹配的 `family=chrome,type=extension` browser，再用 `cua.getTab(...)` 接管既有 creator Tab。保留绑定，完整读取接管返回的 browser/Tab 文档。基础 CUA AX 接口只是入口：文档列出的 `tab.playwright`、`waitForEvent("filechooser")` 和 chooser `setFiles()` 都属于原 Chrome extension Tab；接口名称不表示切换到独立的 `playwright-mcp` 传输。

按当前文档声明的访问方式读取 `file-uploads` 专题。文档缺段、截断或绑定未取得时，同轮补读/恢复一次；可用已声明的 `tab.playwright.domSnapshot()` 无副作用确认页面绑定，不为能力验证打开 chooser 或上传文件。不猜方法、不反射枚举、不另建浏览器客户端。只有完整文档确无能力，或正确绑定明确返回 unsupported，且恢复已耗尽时，才记 `blocked / chrome_extension_filechooser_api_unavailable`，附 `documentationRefs`、`capabilityEvidence`、原始错误及 `documentationRecoveryCount`。超时、AX 点击无变化和缺旧工具名都不是能力缺失证据。

## 先判定已有副作用

- 已提交、审核中、成功或提交结果不明：只读作品管理对账，不上传、不点击发布。
- 用户已上传、已有正确视频或正在处理：复用并完成预览验收，不再触发 chooser。
- 空上传页且检查点确认没有未知选择/上传副作用：核对 canonical 绝对路径、指纹及锁后才上传。
- upload intent 后中断但没有回执：先读页面，不把次数重置为 0。

## 事件先于触发，选择与验收分开

根据本轮 DOM 定位唯一可用的上传按钮、可交互 file input 或关联 label；不固定序号、不强制点击隐藏 input、不走原生窗口/坐标。以下仅在当前文档声明这些签名时使用；`tab`、`trigger`、`canonicalPath` 必须来自本轮绑定和预检：

```javascript
const pending = tab.playwright.waitForEvent("filechooser", { timeoutMs: 10000 })
  .then(chooser => ({ chooser }), error => ({ error }));
let triggerError;
try { await trigger.click({ timeoutMs: 6000 }); }
catch (error) { triggerError = error; }
const event = await pending; // 始终收拢等待，避免未处理拒绝。
if (!triggerError && event.chooser) {
  // 调用前记 selection intent；返回后记 receipt；抛错先只读核验。
  await event.chooser.setFiles([canonicalPath], { timeoutMs: 10000 });
}
```

`setFiles` 成功只证明文件已交给页面控件。继续等待平台上传/处理完成，复读编辑器和预览。没有 chooser、未选文件且复读仍为空时，可在同一 Tab 重定位触发器一次；两次仍失败记 `blocked / file_upload_control_unavailable`。选择已尝试、处理中或选择结果未知时，不重传，保留 `unknown / upload_unconfirmed` 并只读恢复。只有工具明确报权限拒绝才按权限专题处理；不从超时猜权限或 OS 锁屏。

## 预览不止看 AX

AX 没有时长、播放或声音字段时，用已声明的同一 Tab DOM 读取页面实际 `video` 元素，例如：

```javascript
const videos = await tab.playwright.evaluate(() =>
  Array.from(document.querySelectorAll("video")).map(v => ({
    duration: v.duration, currentTime: v.currentTime, readyState: v.readyState,
    paused: v.paused, muted: v.muted, volume: v.volume,
    width: v.videoWidth, height: v.videoHeight, errorCode: v.error?.code ?? null
  }))
);
```

按 DOM 定位当前预览的可见播放控件，用同一 Tab locator 操作后复读时间推进；不在 evaluate 中改变页面或调用隐藏播放器接口。将页面时长/画面与 canonical 验收记录对应，音乐视频保留音频轨和非静音证据。`muted=false` 不是“实际听过声音”的证据，静止缩略图不是可播放证据；当前预览仍无法验收则记录缺失证据并保留草稿，不伪称通过。

## 成稿、下载权限与提交结算

沿用主技能 copyPlan、最近5条轮换及富文本清空后一次写入流程。提交前复读标题、全文、预览、账号、公开/立即发布，以及 `允许=false / 不允许=true`。自定义 checkbox setter 返回不代表切换成功，必要时按当前 DOM 点击语义“不允许”控件再读实际状态。

最终唯一、可见、可用的精确“发布”控件仅点击一次。先记 submit intent，返回后记回执；点击后短暂无提示或仍停留编辑页时，先读 URL/DOM，不再次点击。作品管理异步列表/总数可能滞后：用同一 Tab 可见搜索框搜索本条，唯一匹配标题、全文、时长、发布时间及“审核中/已发布”即可结算；总数未增加不推翻完整条目证据。最多按配置只读刷新；结果未知保留页和状态，不重发。

检查点保存 `triggerKind`、`chooserObserved`、`selectionAttempted`、`selectionReceipt`、`platformMediaEvidence`、`previewEvidence`、`publishClicks`、`recoveryCount`、`reasonCode`、`nextAction` 和 `resumeCondition`。发布回执先持久化，再由 media-ops 完成全部账本写回；账本中断只恢复写回。成功回写后按主技能清理本轮临时页。
