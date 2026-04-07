# Kimi Skills

个人 Kimi Code CLI Skills 集合

## Skills 列表

| Skill | 描述 |
|-------|------|
| hexo-push | 读取 Clippings 目录文章，自动转换为 Hexo 格式并发布 |
| upgrade-kimi-cli | 自动检测并升级 Kimi CLI 到最新版本 |

## 安装方法

### 方式一：直接克隆（推荐）

```bash
git clone https://github.com/askairo/kairo-skills.git ~/.config/agents/skills
```

### 方式二：作为项目级 Skill

在你的项目根目录：
```bash
mkdir -p .agents/skills
cp -r /path/to/kairo-skills/<skill-name> .agents/skills/
```

### 方式三：Git 子模块

```bash
git submodule add https://github.com/askairo/kairo-skills.git .agents/skills/kairo-skills
# 然后在 .agents/skills/ 创建软链接或复制需要的 skill
```

## 目录结构

```
kairo-skills/
├── README.md
├── hexo-push/
│   ├── SKILL.md
│   └── scripts/
│       └── publish.py
├── upgrade-kimi-cli/
│   ├── SKILL.md
│   └── scripts/
│       └── upgrade.py
└── [future-skills]/
    └── ...
```

## 使用 Skill

安装后，在 Kimi Code CLI 中直接描述你的需求即可：

```
发布最新文章
```

```
升级 kimi cli
```

Kimi 会自动识别并触发对应的 skill。

## 更新日志

- 2026-04-07: 添加 upgrade-kimi-cli skill
- 2026-04-07: 初始化仓库，添加 hexo-push skill
