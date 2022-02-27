Creazione progetto

esempio:
progettto: prodigi_html
witnes: padova
witnes: venezia

---------------------------------------------------
Crea la struttura del progetto per padova e venezia

teiprjhtmlmake.py  prodigi_html padova

teiprjhtmlmake.py  prodigi_html venezia
---------------------------------------------------
Nella dir 
prodigi_html/teimcfg

copiare da xteixml2html/teimcfg i files 

html.csv
teimoverflow.csv
-------------------------------------------------------

Nelle dir

prodigi_html/xml/firenze
prodigi_html/xml/padova
prodigi_html/xml/venezia

copiare i file TEI_XML dela relativa witness

======================================
Esecuzione del progetto

situarsi nella dir prodigi_html
lanciare:

prjmgr.py prj/firenze.json

prjmgr.py prj/padova.json

prjmgr.py prj/venezia.json
------------------------------------------
per ogni witness sono eseguite le seguenti operaziopni

prjmgr.py prj/padova_xml.json
prjmgr.py prj/padova_syn.json
prjmgr.py prj/padova_syn_pannel.json
prjmgr.py prj/padova_txt.json
prjmgr.py prj/padova_txt_pannel.jso

INPUT
flori_html/xml/padova.xml

OUTPUT
flori_html/html/padova/txt/padova.html
flori_html/html/padova/txt/eps01.html
..
flori_html/html/padova/txt/eps0n.html

flori_html/html/padova/syn/padova.html
flori_html/html/padova/syn/eps01.html
..
flori_html/html/padova/syn/eps0n.html

================================
elaborazioni singole
================================
prjmgr.py prj/padova_xml.json
esegue:
splitteixml.py -i xml/padova.xml -o xml/padova/ -m padova
-------------------------------
prjmgr.py prj/padova_syn.json

writehtml.py \
-o html/padova/syn/$F.html \
-i '<div id=\padova_dipl_id\ class=\text_pannel tei_dipl\>' \
-wa w

teixml2html.py \
-i xml/padova/$F.xml \
-o html/padova/syn/$F.html \
-c prj_teimcfg/padova_dipl_syn.json \
-wa a 

writehtml.py \
-o html/padova/syn/$F.html \
-i '</div><div id=\padova_int_id\ class=\text_pannel tei_int\>' \
-wa a

teixml2html.py
-i xml/padova/$F.xml
-o html/padova/syn/$F.html
-c prj_teimcfg/padova_inter_syn.json
-wa a 

writehtml.py
-o html/padova/syn/$F.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/padova_syn_pannel.json
 
writehtml.py
-o html/tor1/syn/tor1.html
-i '<div id=\tor1_dip_id\ class=\text_pannel tei_dip\>'
-wa w

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/syn/tor1.html
-c prj_teimcfg/list_dipl_syn.json
-wa a

writehtml.py
-o html/tor1/syn/tor1.html
-i '</div>
<div id=\tor1_int_id\ class=\text_pannel tei_int\>'
-wa a

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/syn/tor1.html
-c prj_teimcfg/list_inter_syn.json
-wa a

writehtml.py
-o html/tor1/syn/tor1.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/padova_txt.json

writehtml.py \
-o html/padova/txt/$F.html \
-i '<div id=\padova_dipl_id\ class=\text_pannel tei_dipl\>' \
-wa w

teixml2html.py \
-i xml/padova/$F.xml \
-o html/padova/txt/$F.html \
-c prj_teimcfg/padova_dipl_txt.json \
-wa a 

writehtml.py \
-o html/padova/txt/$F.html \
-i '</div><div id=\padova_int_id\ class=\text_pannel tei_int\>' \
-wa a

teixml2html.py
-i xml/padova/$F.xml
-o html/padova/txt/$F.html
-c prj_teimcfg/padova_inter_txt.json
-wa a 

writehtml.py
-o html/padova/txt/$F.html
-i '</div>'
-wa a
-------------------------------
prjmgr.py prj/padova_txt_pannel.json
 
writehtml.py
-o html/tor1/txt/tor1.html
-i '<div id=\tor1_dip_id\ class=\text_pannel tei_dip\>'
-wa w

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/txt/tor1.html
-c prj_teimcfg/list_dipl_txt.json
-wa a

writehtml.py
-o html/tor1/txt/tor1.html
-i '</div>
<div id=\tor1_int_id\ class=\text_pannel tei_int\>'
-wa a

teixml2html.py
-i xml/tor1/tor1_list.xml
-o html/tor1/txt/tor1.html
-c prj_teimcfg/list_inter_txt.json
-wa a

writehtml.py
-o html/tor1/txt/tor1.html
-i '</div>'
-wa a
======================================
files dei arametri per le singole applicazioni in
flori_html/prj_teimcfg
=======================================
padova_dipl_syn.json
{
  "html_params": {
    "_WTN_": "padova",
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:syn",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
padova_dipl_txt.json
{
  "html_params": {
    "_WTN_": "padova",
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:txt",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
padova_inter_syn.json
{
  "html_params": {
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:syn",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
padova_inter_txt.json
{
  "html_params": {
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:txt",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
list_dipl_syn.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:syn",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
list_dipl_txt.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d",
  "dipl_inter": "d",
  "before_id": "d"
}
--------------------------------------
list_inter_syn.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i:syn",
  "dipl_inter": "i",
  "before_id": "i"
}
--------------------------------------
list_inter_txt.json
{
  "html_params": {
    "text_null": "",
    "<null>": "",
    "</null>": ""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "i",
  "dipl_inter": "i",
  "before_id": "i"
}
