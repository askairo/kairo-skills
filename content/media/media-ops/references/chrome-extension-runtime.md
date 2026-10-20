# Chrome extension：从外层入口取得完整 Tab API

适用于已配置 `chrome-mcp`、当前工具文档同时提供 `cua` 与 `agent.browsers` 的运行时。只沿用已核验的 extension browser 和目标 Tab，不改传输、Profile 或账号。

## 两层接口与 optional capabilities

- `cua.getState()` / `cua.getTab(...)` 是统一入口。外层 `Tab` 清单可能仅有 AX、截图和基本输入。
- 所选 browser 返回的完整文档若声明 `agent.browsers.*`、`agent.documentation.get(...)` 和 `Tab.playwright`，这些就是当前可调用的接口；不能因为外层类型未列出它们而忽略，也不能把文档里明确提供的 `agent` 当成不可用。
- `tab.capabilities.list()` 只列 optional capabilities。仅返回 `pageAssets` 不表示核心 `playwright`、filechooser 或上传接口缺失。

## 取得同一 browser / Tab 的绑定

首次按任务要求单独读取 `cua.getState()`，匹配配置的 `family=chrome,type=extension` browser 和既有目标 Tab，并通过 `cua.getTab(...)` 实读身份。随后阅读完整所选 browser 文档。

以下代码仅在当前文档声明这些接口时使用；`browserId`、`targetTabId` 均来自本轮 inventory：

```javascript
const browserApi = await agent.browsers.get(browserId);
await browserApi.nameSession("📝 发布任务");
const existing = (await browserApi.user.openTabs())
  .find(item => item.id === targetTabId);
if (!existing) throw new Error("Exact user Tab missing; refresh inventory");
const pageTab = await browserApi.user.claimTab(existing);
await agent.documentation.get("file-uploads");
const state = await pageTab.playwright.domSnapshot();
```

这是在同一 extension 连接取得完整绑定，不是切换到 Playwright MCP、CDP 或原生窗口。复用此绑定；仅在失效时按当前文档恢复。

`browserApi.tabs.get(id)` 面向当前已接管的 agent Tab。若报告 `Existing tabs: none`，先用同一 browser 的 `user.openTabs()` 找到 exact user Tab，再 `user.claimTab(...)`；不能据此报告没有登录 Tab 或 `profile_route_missing`。异步初始化抛错后，变量声明可能没有完成；恢复时重新声明绑定，不能直接给未声明变量赋值。

## 上传缺失必须有正确绑定的证据

上传前实际读取 `file-uploads` 专题，确认当前声明的 `pageTab.playwright.waitForEvent("filechooser")` 和 chooser `setFiles(...)`。注册 chooser 等待后再点本轮定位的上传控件，沿用目标 canonical 文件；具体步骤由平台上传协议负责。

外层缺属性、专题尚未读取、绑定未完成、`tabs.get` 找不到尚未接管的 user Tab、或 optional capabilities 未列核心 API，均只属于 `binding_incomplete`，不能结算 `chrome_extension_filechooser_api_unavailable`。在本轮修复绑定并从原目标的最小阶段继续。只有正确绑定明确返回 unsupported，或完整当前文档确实没有支持入口，才记录真实能力阻断。

能力证据记录：`browserId`、`extensionInstanceId`、exact Tab ID、已读完整文档及专题、`bindingApiRef`、chooser/setFiles 签名、真实调用回执或明确 unsupported。成功取得绑定后纠正先前误判；不保留“等待运行时升级”这种已失效的恢复条件。
