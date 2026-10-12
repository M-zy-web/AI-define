# -*- coding: utf-8 -*-
import fitz

dst = r"c:\Users\chenqx\Desktop\ai-define-master\ai-define-master\m5\datasets\tabulations\sdtm\acrf.pdf"
doc = fitz.open(dst)
toc = doc.get_toc(simple=False)
print("toc entries:", len(toc))
for i, item in enumerate(toc):
    lvl, title, page = item[0], item[1], item[2]
    print(f"{i}\tL{lvl}\tp{page}\t{title}")
doc.close()
