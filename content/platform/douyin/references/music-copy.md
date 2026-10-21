# 音乐文案：帮助听众进入音乐

适用于音乐视频的标题/正文改编与生硬文案修复。账号风格和文案长度由 `~/.agents/local-config/media-ops/config.yaml` 中对应账号的 copyContract 选择；不得把某账号的固定句式推广给所有账号。

## 内容选择

- 首先让人知道听谁、听哪首。正文通常1–2句，按需要可只写一条自然的介绍；不为填字段描述衣服、眼镜、背带、家具、时长或音视频轨。与音乐体验无关的正确事实也可以省略。
- 听歌邀请、曲名入口、已核验的版本关系、确有价值的来源背景都可选。无需每条都给推荐理由或引导互动；问题须与本歌相关、容易回答，不堆“你觉得呢/评论区告诉我”。
- 只表达编辑邀请（如“来听听这个版本”），不预设观众感受、不编故事或歌词含义；避免“治愈所有疲惫/听哭了/开口跪”等无依据效果断言。介绍应自然，不写成证据卡或算法钩子检查表。
- 改编细节只有实际听辨或可靠来源证据支持时才写。截图、波形、响度、编码/轨道、字幕、歌词和标题都不能证明嗓音质感、咬字、颤音、和声、速度变化或编曲感受。不得把静音检测称作听过。无法听辨就记录 audioReview.status=not_listened，不推断声音评价；简单的已核验吉他弹唱身份可保留。
- 原创性、词曲归属和授权仍遵守资产factBoundary。内部证据可记录来源自称，不必每条把“原视频标题/简介标注”写给观众；需要版本关系时按来源可支持的程度表达。

## 合同v2及字段

copyContract.version=2：title要求artist/songTitle，angle可选，maxChars=30；caption只要求author/songTitle，maxChars保留平台上限，推荐1–2句。顺序自由，不强制supportedFact或neutralPerformanceVerb。所有实际写入的事实仍必须有依据。

copyPlan保留title、caption、selectedAngle（编辑切入点，不等于声音评价）、recentCopyRefs（至少5条已发布/已提交成稿）、recentCopies、avoidedPatterns；批量备货另存earlierQueuedCopies并逐项比较。可读性检查关注“是否只是换歌名套同一骨架”，不靠堆物件和同义词替换避重。发布前重新比较实际最近窗口，预备文案不豁免最终核验。

audioReview至少有status（listened/not_listened）和basis；listened须另有实际听辨方式、覆盖时间段和具体发现的时间点。not_listened不能出现听感主张。content asset共同事实与平台copyPlan分开，改写不能改变来源、版权、媒体指纹或队列序号。

长标题先移除可选angle，尽量完整保留英文曲名；仍超30字可使用明确标记为编辑译名的自然中文名，正文保留完整英文，内部titleLocalization注明非官方译名。无可靠译名时保留待处理，不用机械截断或逐词硬译。无需在公开标题加入冗长“（暂译）”占位语，是否公开披露按误导风险判断。

## 改写与审计

只改ready/pending等尚未发布目标；submitted/uncertain先对账，已发布正文不借此批量改写。每项把旧copyPlan、adaptationNotes、版本和改写原因加入copyHistory，再同步资产顶层及目标copyPlan。只更新当前可执行copyPlan，不篡改旧运行证据。Markdown当前队列与registry置顶标出新版本，旧文案保留历史并声明已替代。队列顺序、视频路径、哈希、plannedAt和发布状态不变。

验收时检查30字标题、作者/完整曲名可辨、无外链和未经核验的原创/声音主张、历史与队列内避重、顶层/目标文案一致、旧稿可追溯。简短事实不足不再因缺“额外具体事实”阻止ready。
