#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立脚本：从 YAML 生成 Define-XML 2.1（v3）
- 以 build_define_v2.ipynb 当前 build_define 单元逻辑为准
- 数据集顺序按 datasets/toc.yaml 读取，并按 Class 规范顺序归一化
- 不手工写 xmlns，避免重复命名空间
"""

import os
import time
import unicodedata
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError as exc:
    raise SystemExit("缺少依赖 pyyaml，请先安装: pip install pyyaml") from exc


WORK_DIR = Path(r"C:\工作文件\项目\SHR-A1811-306\ai-define-master\ai-define-master")
assert WORK_DIR.exists(), f"WORK_DIR 不存在: {WORK_DIR}"
os.chdir(WORK_DIR)

_t0 = time.time()

CFG = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {}
LANG = str(CFG.get("language", "CN")).upper()
assert LANG in ("CN", "EN"), f"config.language 必须是 CN 或 EN，当前: {LANG!r}"
XML_LANG = {"CN": "zh", "EN": "en"}[LANG]

SDTM_DIR = CFG["sdtm_dir"]
DATASETS_DIR = CFG["output_files"]["datasets_dir"]
STUDY_DIR = Path(CFG.get("study_dir", "study_std"))
DEFINE_XML = CFG["output_files"]["define_xml"]

CODELISTS_YAML = STUDY_DIR / "codelists.yaml"
OUT_METHODS_YAML = STUDY_DIR / "methods.yaml"
OUT_COMMENTS_YAML = STUDY_DIR / "comments.yaml"
STUDY_YAML = STUDY_DIR / "study.yaml"
TOC_YAML = Path(DATASETS_DIR) / "toc.yaml"


def _w(text):
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in str(text))


def _pad(text, width):
    text = str(text)
    return text + " " * max(0, width - _w(text))


ODM = "http://www.cdisc.org/ns/odm/v1.3"
DEF = "http://www.cdisc.org/ns/def/v2.1"
XLINK = "http://www.w3.org/1999/xlink"
XML = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("", ODM)
ET.register_namespace("def", DEF)
ET.register_namespace("xlink", XLINK)


def o(tag):
    return f"{{{ODM}}}{tag}"


def d(tag):
    return f"{{{DEF}}}{tag}"


def load(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def SE(parent, tag, text=None, **attrs):
    elem = ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items() if v is not None})
    if text is not None:
        elem.text = str(text)
    return elem


def TT(parent, text, lang=XML_LANG):
    if text is None:
        return
    desc = SE(parent, o("Description"))
    SE(desc, o("TranslatedText"), text, **{f"{{{XML}}}lang": lang})


IGoid = lambda dom: f"IG.{dom}"
IToid = lambda dom, var: f"IT.{dom}.{var}"
VLoid = lambda dom, var: f"VL.{dom}.{var}"
WCoid = lambda dom, var, idx: f"WC.{dom}.{var}.V{idx}"
VITo = lambda dom, var, idx: f"IT.{dom}.{var}.V{idx}"
CLoid = lambda key: f"CL.{key}"
MToid = lambda key: f"MT.{key}"
COMoid = lambda key: f"COM.{key}"

CLASS_ORDER_EN = [
    "TRIAL DESIGN", "SPECIAL-PURPOSE", "INTERVENTIONS", "EVENTS",
    "FINDINGS", "FINDINGS ABOUT", "RELATIONSHIP", "STUDY REFERENCE",
]
CLASS_ORDER_ZH = {
    "试验设计类": "TRIAL DESIGN",
    "b'k类": "SPECIAL-PURPOSE",
    "干预类": "INTERVENTIONS",
    "事件类": "EVENTS",
    "发现类": "FINDINGS",
    "发现关于": "FINDINGS ABOUT",
    "关系类": "RELATIONSHIP",
    "研究参考类": "STUDY REFERENCE",
}


def normalize_dataset_class(value):
    if value is None:
        return ""
    text = str(value).strip()
    return CLASS_ORDER_ZH.get(text, text).upper()


def class_rank(value):
    try:
        return CLASS_ORDER_EN.index(normalize_dataset_class(value))
    except ValueError:
        return len(CLASS_ORDER_EN)


print("\n" + "═" * 58)
print("  ✅ Define-XML 2.1 独立生成脚本 (v3)")
print("═" * 58)
print(f"  📁 {_pad('工作目录', 8)}{WORK_DIR}")
print(f"  🌐 {_pad('语言', 8)}{LANG}   ·   xml:lang={XML_LANG}")
print(f"  📂 {_pad('数据目录', 8)}{SDTM_DIR}")
print(f"  📤 {_pad('输出', 8)}{DEFINE_XML}")
print("─" * 58)

study = load(STUDY_YAML)
STD_IG = next((s["oid"] for s in study.get("standards", []) if s.get("type") == "IG"), "SDTM-IG")
STD_CT = next(
    (s["oid"] for s in study.get("standards", []) if s.get("type") == "CT" and s.get("publishing_set") == "SDTM"),
    "SDTM-CT",
)
codelists = load(CODELISTS_YAML) or {}
methods = load(OUT_METHODS_YAML) or {}
comments = load(OUT_COMMENTS_YAML) or {}

DS_DIR = Path(DATASETS_DIR)
OUT_FILE = Path(DEFINE_XML)
toc_entries = load(TOC_YAML) or []
toc_loaded = []
for idx, entry in enumerate(toc_entries):
    if not isinstance(entry, dict):
        continue
    dom = entry.get("dataset")
    if not dom:
        continue
    toc_loaded.append((idx, dom, entry.get("Class")))
toc_loaded.sort(key=lambda item: (class_rank(item[2]), item[0]))
toc_order = [dom for _, dom, _ in toc_loaded]

ds_blocks = []
_skip_toc = []
supp_blocks = []
for dom in toc_order:
    fp = DS_DIR / f"{dom.lower()}.yaml"
    if not fp.exists():
        _skip_toc.append(dom)
        continue
    blk = load(fp)
    ds_blocks.append((blk, False))
    if blk.get("supplemental"):
        supp_blocks.append((blk["supplemental"], True))

ds_blocks.extend(supp_blocks)

IGs, ITs, VLs, WCs = [], [], [], []


def build_origin(parent, origin):
    if not origin:
        return
    elem = SE(parent, d("Origin"), Type=origin.get("type"), Source=origin.get("source"))
    if origin.get("description"):
        TT(elem, origin["description"])
    for pg in origin.get("crf_pages", []):
        doc_ref = SE(elem, d("DocumentRef"), leafID="Annotated CRF")
        SE(doc_ref, d("PDFPageRef"), PageRefs=pg, Type="PhysicalRef")
    for doc in origin.get("documents", []):
        SE(elem, d("DocumentRef"), leafID=doc)



def build_itemdef(oid, name, var_yaml, *, codelist=None, valuelist=None, label=None):
    item = ET.Element(
        o("ItemDef"),
        {
            "OID": oid,
            "Name": name,
            "DataType": str(var_yaml.get("type")),
            "Length": str(var_yaml.get("length")),
            "SASFieldName": name,
        },
    )
    if var_yaml.get("significant_digits"):
        item.set("SignificantDigits", str(var_yaml["significant_digits"]))
    if var_yaml.get("display_format"):
        item.set(d("DisplayFormat"), str(var_yaml["display_format"]))
    if var_yaml.get("comment"):
        item.set(d("CommentOID"), COMoid(var_yaml["comment"]))
    TT(item, label if label is not None else var_yaml.get("label"))
    if codelist:
        SE(item, o("CodeListRef"), CodeListOID=CLoid(codelist))
    build_origin(item, var_yaml.get("origin"))
    if valuelist:
        SE(item, d("ValueListRef"), ValueListOID=valuelist)
    ITs.append(item)
    return item



def process(block):
    dom = block["domain"]
    ig = ET.Element(
        o("ItemGroupDef"),
        {
            "OID": IGoid(dom),
            "Domain": block.get("domain"),
            "Name": dom,
            "Repeating": "Yes" if block.get("repeating") else "No",
            "IsReferenceData": "Yes" if block.get("is_reference_data") else "No",
            "SASDatasetName": block.get("sas_dataset") or dom,
            "Purpose": block.get("purpose") or ("列表" if LANG == "CN" else "Tabulation"),
            d("Structure"): block.get("structure") or "",
            d("StandardOID"): STD_IG,
            d("ArchiveLocationID"): f"LF.{dom}",
        },
    )
    if block.get("has_no_data"):
        ig.set(d("HasNoData"), "Yes")
    if block.get("comment"):
        ig.set(d("CommentOID"), COMoid(block["comment"]))
    TT(ig, block.get("label"))

    for vname, var_yaml in (block.get("variables") or {}).items():
        valuelist_oid = None
        if var_yaml.get("value_list"):
            valuelist_oid = VLoid(dom, vname)
            vl = ET.Element(d("ValueListDef"), {"OID": valuelist_oid})
            for idx, entry in enumerate(var_yaml["value_list"], 1):
                vit_oid = VITo(dom, vname, idx)
                vchild = {"type": var_yaml.get("type"), "length": var_yaml.get("length")}
                build_itemdef(
                    vit_oid,
                    vname,
                    vchild,
                    codelist=entry.get("codelist"),
                    valuelist=valuelist_oid,
                    label=entry.get("label"),
                )
                vit = ITs[-1]
                if entry.get("origin"):
                    build_origin(vit, entry["origin"])
                if entry.get("comment"):
                    vit.set(d("CommentOID"), COMoid(entry["comment"]))
                ref = SE(
                    vl,
                    o("ItemRef"),
                    ItemOID=vit_oid,
                    OrderNumber=idx,
                    Mandatory="Yes" if entry.get("mandatory") else "No",
                    MethodOID=MToid(entry["method"]) if entry.get("method") else None,
                )
                where_oid = WCoid(dom, vname, idx)
                SE(ref, d("WhereClauseRef"), WhereClauseOID=where_oid)
                wc = ET.Element(d("WhereClauseDef"), {"OID": where_oid})
                for cond in entry.get("where", []):
                    rc = SE(
                        wc,
                        o("RangeCheck"),
                        SoftHard="Soft",
                        **{d("ItemOID"): IToid(dom, cond["variable"]), "Comparator": cond.get("comparator")},
                    )
                    for val in cond.get("values", []):
                        SE(rc, o("CheckValue"), val)
                WCs.append(wc)
            VLs.append(vl)
            build_itemdef(IToid(dom, vname), vname, var_yaml, valuelist=valuelist_oid)
        else:
            build_itemdef(IToid(dom, vname), vname, var_yaml, codelist=var_yaml.get("codelist"))
        SE(
            ig,
            o("ItemRef"),
            ItemOID=IToid(dom, vname),
            OrderNumber=var_yaml.get("order"),
            Mandatory="Yes" if var_yaml.get("mandatory") else "No",
            KeySequence=var_yaml.get("key_sequence"),
            MethodOID=MToid(var_yaml["method"]) if var_yaml.get("method") else None,
        )

    SE(ig, d("Class"), Name=block.get("class"))
    leaf = SE(
        ig,
        d("leaf"),
        ID=f"LF.{dom}",
        **{f"{{{XLINK}}}href": block.get("archive") or f"{dom.lower()}.xpt"},
    )
    SE(leaf, d("title"), block.get("archive") or f"{dom.lower()}.xpt")
    IGs.append(ig)


for block, _ in ds_blocks:
    process(block)

file_meta = study.get("file", {})
root_attrs = {
    "ODMVersion": file_meta.get("odm_version", "1.3.2"),
    "FileOID": file_meta.get("file_oid", study["study"]["oid"]),
    "FileType": "Snapshot",
    "CreationDateTime": file_meta.get("creation_datetime"),
    "Originator": file_meta.get("originator"),
    "SourceSystem": file_meta.get("source_system"),
    "SourceSystemVersion": file_meta.get("source_system_version"),
    d("Context"): file_meta.get("context", "Submission"),
}
root = ET.Element(o("ODM"), {k: str(v) for k, v in root_attrs.items() if v is not None})
st = SE(root, o("Study"), OID=study["study"]["oid"])
gv = SE(st, o("GlobalVariables"))
SE(gv, o("StudyName"), study["study"]["name"])
SE(gv, o("StudyDescription"), study["study"]["description"])
SE(gv, o("ProtocolName"), study["study"]["protocol"])
mv = SE(
    st,
    o("MetaDataVersion"),
    OID=study["metadata_version"]["oid"],
    Name=study["metadata_version"]["name"],
    Description=study["metadata_version"].get("description"),
    **{d("DefineVersion"): study["metadata_version"]["define_version"]},
)

stds = SE(mv, d("Standards"))
for std in study.get("standards", []):
    attrs = {
        "OID": std["oid"],
        "Name": std["name"],
        "Type": std["type"],
        "Version": std["version"],
        "Status": std.get("status"),
        "PublishingSet": std.get("publishing_set"),
    }
    if std.get("comment"):
        attrs[d("CommentOID")] = COMoid(std["comment"])
    SE(stds, d("Standard"), **attrs)

docs = study.get("documents", {})
if docs.get("annotated_crf"):
    SE(SE(mv, d("AnnotatedCRF")), d("DocumentRef"), leafID=docs["annotated_crf"]["leaf_id"])
if docs.get("supplemental"):
    sd = SE(mv, d("SupplementalDoc"))
    for meta in docs["supplemental"]:
        SE(sd, d("DocumentRef"), leafID=meta["leaf_id"])

for elem in VLs:
    mv.append(elem)
for elem in WCs:
    mv.append(elem)
for elem in IGs:
    mv.append(elem)
for elem in ITs:
    mv.append(elem)

for key, cl in codelists.items():
    elem = SE(mv, o("CodeList"), OID=CLoid(key), Name=cl.get("name"), DataType=cl.get("data_type", "text"))
    elem.set(d("StandardOID"), cl.get("standard", STD_CT))
    if cl.get("type") == "external":
        SE(elem, o("ExternalCodeList"), Dictionary=cl["dictionary"], Version=cl["version"], href=cl.get("href"))
    else:
        item_tag = "CodeListItem" if cl.get("type") == "decoded" else "EnumeratedItem"
        for item in cl.get("items", []):
            ci = SE(elem, o(item_tag), CodedValue=item["value"])
            if item.get("extended"):
                ci.set(d("ExtendedValue"), "Yes")
            if "decode" in item:
                dec = SE(ci, o("Decode"))
                SE(dec, o("TranslatedText"), item["decode"], **{f"{{{XML}}}lang": XML_LANG})
            if item.get("nci_code"):
                SE(ci, o("Alias"), Name=item["nci_code"], Context="nci:ExtCodeID")
    if cl.get("nci_code"):
        SE(elem, o("Alias"), Name=cl["nci_code"], Context="nci:ExtCodeID")

for key, method in methods.items():
    me = SE(mv, o("MethodDef"), OID=MToid(key), Name=method.get("name"), Type=method.get("type", "Computation"))
    TT(me, method.get("description"))

for key, comment in comments.items():
    ce = SE(mv, d("CommentDef"), OID=COMoid(key))
    if isinstance(comment, dict):
        TT(ce, comment.get("description"))
        if comment.get("doc_id"):
            dr = SE(ce, d("DocumentRef"), leafID=comment["doc_id"])
            if comment.get("page_refs"):
                SE(dr, d("PDFPageRef"), PageRefs=str(comment["page_refs"]), Type=comment.get("page_ref_type", "PhysicalRef"))
    else:
        TT(ce, comment)

for _, meta in [("annotated_crf", docs.get("annotated_crf"))] + [("supp", x) for x in docs.get("supplemental", [])]:
    if not meta:
        continue
    leaf = SE(mv, d("leaf"), ID=meta["leaf_id"], **{f"{{{XLINK}}}href": meta.get("href")})
    SE(leaf, d("title"), meta.get("title"))

ET.indent(root, space="  ")
xml_body = ET.tostring(root, encoding="unicode")
header = '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="./define2-1.xsl"?>\n'
OUT_FILE.write_text(header + xml_body, encoding="utf-8")

chk = ET.parse(OUT_FILE).getroot()


def cnt(tag):
    return len(chk.findall(".//" + tag))


defined = {elem.get("OID") for elem in chk.iter() if elem.get("OID")}
REF_ATTRS = {"ItemOID", "CodeListOID", "ValueListOID", "WhereClauseOID", "MethodOID", "CommentOID", "leafID"}
leaf_ids = {elem.get("ID") for elem in chk.iter() if elem.tag == d("leaf")}
broken = []
for elem in chk.iter():
    for attr, value in elem.attrib.items():
        attr_name = attr.split("}")[-1]
        if attr_name == "leafID":
            if value not in leaf_ids:
                broken.append((attr_name, value))
        elif attr_name in REF_ATTRS and value not in defined:
            broken.append((attr_name, value))


def _sz(path):
    size = os.path.getsize(path)
    return f"{size / 1e6:.1f} MB" if size >= 1e6 else f"{size / 1e3:.1f} KB"


counts = [
    ("ItemGroupDef", o("ItemGroupDef")),
    ("ItemDef", o("ItemDef")),
    ("CodeList", o("CodeList")),
    ("MethodDef", o("MethodDef")),
    ("CommentDef", d("CommentDef")),
    ("ValueListDef", d("ValueListDef")),
    ("WhereClauseDef", d("WhereClauseDef")),
]

print("\n" + "═" * 58)
print("  ✅ Define-XML 2.1 生成完成 (v3)")
print("═" * 58)
print(f"  📤 {_pad('输出', 6)}{OUT_FILE.resolve()}")
print(f"  📐 {_pad('大小', 6)}{_sz(OUT_FILE)}")
print("─" * 58)
print("  🔢 元素统计")
for label, tag in counts:
    note = "   (= 数据集变量 + 值水平条件)" if label == "ItemDef" else ""
    print(f"       · {_pad(label, 16)}{cnt(tag):>5}{note}")
print("─" * 58)
print("  🔗 断链引用    " + ("无 ✅" if not broken else f"{len(broken)} 处 ❌ {broken[:5]}"))
if _skip_toc:
    print(f"  ⚠ 缺域        toc 列了但 datasets/ 缺文件 {len(_skip_toc)} 个: {_skip_toc}")
print(f"  📋 数据集顺序  {toc_order}")
print(f"  ⏱  耗时        {time.time() - _t0:.1f} s")
print("═" * 58)
