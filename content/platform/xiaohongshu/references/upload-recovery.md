# 小红书：同一 Tab 图片上传恢复

此流程只处理小红书图片上传，不变更账号策略或浏览器权限。沿用 `contentId + targetId` 锁、配置通道、已核验账号、既有草稿和 canonical asset；不改用原生选择器、桌面坐标、CDP 或其他浏览器。通道文档建议原生回退时，本媒体流程仍不允许。

## 1. 先确定最小未完成阶段

- 目标已成功、审核中、`publish_unconfirmed`、`uncertain` 或有提交意图但无法确定结果：只读对账，不上传、不发布。
- 编辑器已有正确图片/处理进度：复用该产物，等待或核验，不重新打开上传页，不再 `setFiles`。
- 仅处于空上传页且记录无媒体副作用：完成身份、锁、canonical 路径/指纹预检后进入 chooser。
- 检查点在 `setFiles` 前记录 upload intent，返回后记录 receipt。中断留下 intent、没有 receipt 时，不假定上传次数为0，先读平台页。

## 2. 使用当前运行时明确支持的接口

先读所选浏览器提供的 `file-uploads` 文档；新版接口用 `agent.documentation.get("file-uploads")`（仅当当前文档声明），不猜 `cua.getDocumentation`、`setInputFiles` 或原生接口。通过所选 extension browser 的文档取得同一 Tab 的 `playwright` 绑定；不会因为 wrapper 没有该属性就报路由缺失。

复读 DOM，确认可见“上传图片”按钮唯一且可用，优先精确 role/name 定位。`input[type=file]` 在小红书可能隐藏；隐藏 input 或 AX 的“选择文件”标签不是默认触发器。没有可见按钮时，只能使用当前 DOM 中确实可交互且唯一的 file input/关联 label，不强制点击隐藏 input，不固定 selector、元素序号或坐标。

等待必须在点击前注册，并立即安装 rejection handler，防止 chooser 超时成为未处理拒绝、重置 REPL。同一 Tab 的 helper [upload_once.mjs](../scripts/upload_once.mjs) 接收已绑定 Tab、经本轮 DOM 定位的 trigger 和既有绝对路径；它不选择账号、不导航、不重试、不发布。通过 `cua_repl` 调用，不得在 shell 创建浏览器/调用页面。可在允许模块加载的 REPL 中导入 helper，或按其模式调用当前已声明接口：

```javascript
// tab、trigger、assetPath 均由当前预检/DOM 确认，不复用本文的站点序号。
const pending = tab.playwright.waitForEvent("filechooser", { timeoutMs: 10000 })
  .then(chooser => ({ chooser }), error => ({ error }));
let triggerError;
try { await trigger.click({ timeoutMs: 6000 }); }
catch (error) { triggerError = error; }
const event = await pending; // 即使点击异常也收拢等待，不遗留异步拒绝。
// triggerError 或 event.error：先读状态；不执行 setFiles。
if (!triggerError && event.chooser) {
  try { await event.chooser.setFiles([assetPath], { timeoutMs: 10000 }); }
  catch (error) { /* 记录 selection attempted/unconfirmed；先只读核验，不重传。 */ }
}
```

helper 必须显式传入本轮实读的 `priorState: "empty"` 才允许启动；缺少状态或任何其他状态都只读。`setFiles` 返回成功仅代表文件已交给控件，不代表平台上传或处理已验收。读平台缩略图/图片计数、处理状态及编辑器；处理中时可对当前 DOM 已定位的完成控件使用支持的 `waitFor`（最多30秒）再复读一次，不能无界轮询。确认 canonical 图片内容、实际尺寸与目标一致后才写 `asset_uploaded`，继续填文案。不把已有封面再当新资产上传。

## 3. 有界恢复与分类

| 当前证据 | 决策 |
| --- | --- |
| chooser 未出现，setFiles 未尝试，复读确认空上传页无图片/处理 | `retryable_failure / filechooser_not_opened`；在同一 Tab 重定位可见触发器一次并重新注册等待，不重复无效 AX/隐藏 input 点击。两次触发仍失败，`blocked / file_upload_control_unavailable`。 |
| setFiles 返回成功，平台仍处理或尚未显示图片 | 保留同一页，用状态等待/只读复核媒体处理一次；不能立即判能力缺失或再次选文件。达到处理等待预算仍无明确状态，`unknown / upload_unconfirmed`。 |
| setFiles 抛错，或中断时可能已选文件 | 先只读核验；正确媒体已出现则继续；副作用无法确定为 `unknown / upload_unconfirmed`，不重传。 |
| 工具明确报 file URL permission denied，且能确定未交付文件 | 读取当前 `chrome-file-upload-troubleshooting`；`blocked / file_url_access_denied`，说明当前文档要求的授权方法。不得把单纯 chooser 超时猜成权限未开，更不自动扩大浏览器权限。授权恢复后从该资产的上传阶段重启预检。 |
| 正确图片、计数、处理完成及编辑器明确 | `success / asset_uploaded`；不再上传，复读文案和发布门禁。 |
| 账号不符、验证码/挑战、真实限流 | 记录对应硬阻断，不以重定位、权限修改、换通道或新候选绕过。 |

每次观察只记录当前公开页面和操作结果：`triggerKind`、`chooserObserved`、`selectionAttempted`、`selectionReceipt`、`platformMediaEvidence`、`recoveryCount`、`reasonCode`、`nextAction`、`resumeCondition`。不读取 Cookie、令牌、验证码、浏览器内部会话或 OS 锁屏状态。未知上传副作用不是 `publish_failed`；发布控件仍只能按既有门禁点击一次。

## 离线验收

运行 `node scripts/test_upload_once.mjs`（技能目录内）。测试只使用 fake Tab/chooser，检查事件先于触发、超时收拢、选文件不重复、已有草稿/未知状态拒绝启动；不向任何平台上传或发布。真正平台验收以本轮 live editor/manager 为准，不把 mock 测试当作端到端成功。
