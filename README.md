# AI Define Master — Define-XML 2.1 自动化生成（训练项目）

本项目通过 Jupyter Notebook 流水线，将 **部门级标准库、研究级规格书、SDTM XPT 数据集、注释版 aCRF** 自动组装为符合 CDISC **Define-XML 2.1** 规范的 `define.xml` 文件。

## 流水线

```
[部门标准 xlsx]  [项目规格 xlsx]  [SDTM XPT 数据]  [注释 aCRF PDF]
        │                │               │                │
        ▼                ▼               ▼                ▼
   [中间 YAML 产物（dept_std/ + study_std/ + datasets/）]
        │
        ▼
   define.xml  ──▶  在浏览器中用 define2-1.xsl 查看
```

`build_define_v2.ipynb` 按以下顺序执行（必须 Run All 从头到尾运行）：

1. **读取配置** — `config.yaml`（语言、研究号、输入输出路径）
2. **提取部门/行业标准** — CDISC 受控术语、计算方法库、值级元数据、WhereClause、注释库
3. **提取项目文件** — aCRF、标准码表、SDTM 规格书、域数据集、研究信息
4. **组装 define.xml** — 按域生成最终产物

## 目录结构

| 目录/文件 | 说明 |
|---|---|
| `build_define_v2.ipynb` | 主流水线 Notebook（当前版本） |
| `config.yaml` | 项目配置：研究号、语言、输入输出路径 |
| `dept_std/` | 部门级标准库（SDTM CT 包、计算方法、值级元数据、注释库） |
| `study_std/` | 研究级文件（SDTM 规格书、标准码表） |
| `m5/datasets/tabulations/sdtm/` | SDTM XPT 数据集与注释版 aCRF（本地数据，不入库） |
| `datasets/` | 各域 YAML 中间产物（运行时生成） |
| `define.xml` | 最终产物（Define-XML 2.1） |
| `define2-1.xsl` | Define-XML 2.1 官方渲染样式表（浏览器查看用） |
| `define_src/` | YAML 源文件设计（source-of-truth 方案，见下文） |
| `guidance/新手学习指导.md` | 新成员入门文档（环境准备、运行步骤、常见问题） |
| `archive/` | 历史版本与参考文件（旧版 Notebook、P21 一致性规则等） |
| `demo/` | 演示视频（体积过大，不入库） |

## 快速开始

### 1. 环境准备

- Python 3.9+（推荐 3.10 / 3.11）
- 依赖安装：

```powershell
pip install pyyaml openpyxl pymupdf pyreadstat pandas
```

- 编辑器推荐 VS Code（安装 Python 与 Jupyter 扩展）

### 2. 准备输入文件

- 部门标准库 → `dept_std/`
- 研究级规格书与码表 → `study_std/`
- SDTM XPT 数据集与 aCRF PDF → `config.yaml` 中 `sdtm_dir` 指定的目录
- 修改 `config.yaml`：研究号、语言（CN/EN）、各输入文件名

### 3. 运行

在 VS Code 中打开 `build_define_v2.ipynb`，**Run All**。

### 4. 查看结果

```powershell
python -m http.server 8080
```

浏览器访问 `http://localhost:8080/define.xml`（经 `define2-1.xsl` 渲染）。

> 详细步骤与常见问题排查见 [guidance/新手学习指导.md](guidance/新手学习指导.md)。

## 设计理念（define_src/）

`define_src/` 目录演示了「**YAML 为源、define.xml 为编译产物**」的目标方案：

```
源(YAML) ──确定性生成器──▶ define.xml ──校验(schema + 引用完整性 + P21 规则)
```

核心约定：

1. **不写裸 OID** — 文件中用自然名引用（如 `codelist: MEDDRACT`），OID 由生成器在编译期按「域 + 变量/名称」确定性拼接，从源头消灭断链与拼写错误
2. **按域拆分** — 一个域的全部信息内聚在一个文件；跨域复用的码表/方法/注释抽到共享库
3. **SUPP-- 并入父域** — `SUPPAE` 写在 `ae.yaml` 的 `supplemental:` 段
4. **字段分层** — `label`/`type`/`length` 等可由数据集扫描与 SDTMIG 标准库自动填充；`origin`/`method`/`value_list` 等语义溯源信息由人工（或 AI 起草后人工复核）维护

详见 [define_src/README.md](define_src/README.md)。

## 当前研究

`config.yaml` 默认配置：**SHR-1234-III-301**，输出语言中文（`xml:lang="zh"`）。

## 版本库说明

以下内容已通过 `.gitignore` 排除（保留在本地）：

- SAS 数据集文件（`*.sas7bdat`、`*.xpt`）
- `demo/demo.mp4`（213 MB，超过 GitHub 100 MB 上限）
