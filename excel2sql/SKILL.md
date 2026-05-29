---
name: excel2sql
description: 从 Excel 读取数据并结合 Java Entity 类生成新增 SQL。适用于需要按实体字段落库、批量导入主从数据、并统一审计字段(create_id/create_name/create_by/update_id/update_name/update_by)为 1/admin/超级管理员 的场景。
---

# excel2sql

## 用法

在技能目录执行：

```powershell
node scripts/excel2sql.js --excel <excel路径> --entity <Java实体文件路径> --out <输出sql路径>
```

可选参数：

- `--sheet <sheet名>`：默认第一个 sheet。
- `--strict`：开启严格模式。若 Excel 列找不到对应字段则报错。

## 约定

- 根据实体类读取 `@TableName(value = "...")` 作为目标表名。
- 仅使用实体中真实数据库字段：忽略 `@TableField(exist = false)` 和 `static` 字段。
- 字段名按驼峰转下划线匹配数据库列（例如 `supplierFullName -> supplier_full_name`）。
- Excel 列头支持常见前缀清洗：`*`、空格、全角空格。
- 固定注入审计字段：
  - `create_id = 1`
  - `create_name = '超级管理员'`
  - `create_by = 'admin'`
  - `update_id = 1`
  - `update_name = '超级管理员'`
  - `update_by = 'admin'`

## 输出

- 生成 `INSERT INTO ... VALUES ...;` SQL。
- 对字符串自动转义单引号。
- 空值输出为 `NULL`。

## 注意

- 该脚本不会自动做字典中文标签到 code 的转换；如需转换，请先在 Excel 中提供 code，或在 SQL 里手动补 `select dict_value` 子查询。
- 生成后请先在测试库执行验证。
