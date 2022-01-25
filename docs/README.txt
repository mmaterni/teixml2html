teixml2html.py
    trasforma file xm in file html utilizzando un file di
    csv dve sono definiti le entity per l trasformazione

parametri:

-i file xml 
-o file html

parametri alternativi
- c file di configurazione json
oppure
-w name witnesss
-di d=> diplonatica i=> interpretativa

parametri facoltativi
-wt (default w) modalità di scrittura output 
    a=> append w=> write
-d  (default 0) livelo debug 0/1/2

----------------------------------
es. file di configurazione:
{

  "html_params": {
    "_WTN_": "witnedd",
    "text_null": "",
    "_QA_": "\"",
    "_QC_": "\""
  },
  "html_tag_file": "teimcfg/html.csv",
  "html_tag_type": "d:txt",
  "dipl_inter": "d",
  "before_id": "K"
}

_WTN_ : nome del manoscritto

parametri standars per gestione apici e testo nulo

html_tag_type: path del file dei tag html

dipl_inter: d = diplomatica, i=> interpretativa

before_id: prefisso id

----------------------------------
lancio con file di configurazione:

teixmltohtml.py -i file.xml -o file.html -c file_config.json [-wa a/w] [-d 1/2/3]
---------------------------------------
lancio con parametri:

teixmltohtml.py -i file.xml -o file.html -wt witness - di /d/i  [-wa a/w] [-d 1/2/3]

Il file di configurazione viene automaticamete creato con
alcuni valori di default:

html_tag_file: teimcfg/html.csv
html_tag_type: d:txt
dipl_inter: d
before_id": K

il file json può essere modificto  per un successivo lanco



