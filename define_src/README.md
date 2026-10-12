# Define-XML 源（YAML）— SHR-A1811-III-306

本目录是把 `define.xml` 反向拆解出的 **YAML 源（source-of-truth）**。
设计目标：把 define.xml 当「编译产物」，YAML 当「可被人 / AI 编辑、可进 GitLab、可校验」的源。

```
源(YAML) ──确定性生成器──▶ define.xml ──校验(schema + 引用完整性 + P21规则)
```

## 目录结构

```
define_src/
├─ study.yaml          研究级：标识、标准版本、外部文档(aCRF等)、字典版本
├─ codelists.yaml      共享码表库（188 个：解码型/枚举型/外部字典），按 key 引用
├─ methods.yaml        共享派生方法库（38 个），按 key 引用
├─ comments.yaml       共享注释库（68 个），按 key 引用
├─ datasets/
│   ├─ dm.yaml  ae.yaml  lb.yaml ...   每个域一个文件（34 个）
│   └─ （21 个 SUPP-- 已并入各自父域文件的 supplemental: 段）
└─ README.md
```

## 设计约定（重要）

1. **不写裸 OID。** 文件里一律用自然名引用：`codelist: MEDDRACT`、`method: DY`、
   `comment: MEDDRA`。`IT.AE.AEDECOD`、`CL.MEDDRACT` 这类 OID 由生成器在编译期
   按 `域 + 变量 / 名称` 确定性拼出，并负责把所有引用连好、保证唯一与闭环。
   → 人和 AI 永远碰不到 OID，从源头消灭「断链 / OID 打错字」这类错误。

2. **按「域」拆，不按 Define 元素类型拆。** 一个域的全部信息内聚在一个文件，
   改一个域只动一个文件。跨域复用的码表 / 方法 / 注释抽到共享库，避免重复。

3. **SUPP-- 并入父域。** `SUPPAE` 在 `ae.yaml` 的 `supplemental:` 段里，
   其 `QVAL` 的 QNAM 取值规则在 `value_list` 中。

4. **value_list = 值水平元数据(VLM)。** 形如「在某条件(where)下，该变量用哪个码表 /
   什么 origin」。本研究共 269 条值水平条件。

## 字段分层：哪些将来「自动」、哪些「需人工」

反向拆解为了忠实，把字段都填上了。但在正式生成器里，字段分两层：

| 层 | 字段 | 生产环境来源 |
|---|---|---|
| **自动**（无需手维护） | `label` `type` `length` `display_format` `significant_digits` `order` `mandatory` `key_sequence` `archive` | dataset-scan 的 metadata.json + SDTMIG 标准库 |
| **自动**（研究级） | `study` `standards` `dictionaries` 部分 | TS 域 + 项目配置 |
| **人工 / AI 起草后人复核** | `origin`（尤其 `crf_pages`）、`method`、`codelist` 的 decode、`value_list` 的 where、`comment` | 人类知识 / aCRF / SAP |

→ 真正要团队维护的，只有最后一行那批语义 / 溯源信息。其余编译期合并即可。

## 往返完整性

- 数据集 55（34 主 + 21 SUPP）✅
- 变量 880（数据集变量）+ 值水平条件 269 = 1149（= 原 ItemDef 总数）✅
- 码表 188 ✅ 方法 38 ✅ 注释 68 ✅

## 下一步（生成器）

写一个确定性 `build.py`：读取本目录 YAML + metadata.json → 拼 OID、连引用 →
输出 define.xml → 跑 schema / 引用完整性校验。YAML 改动走 GitLab，define.xml 作为
发布产物。AI 只编辑 YAML（安全、语义层），不直接碰 XML。
