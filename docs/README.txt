teixml2html.py
    trasforma file xm in file html utilizzando un file di
    csv dve sono definiti le entity per l trasformazione

parametri:

-i file xml 
-o file html
-c file di configurazione json
-wa a)append w)write modalità di scrittura output 
    defailt:w
-d  livelo debug 0/1/2
    default:0

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

parametri standards per gestione apici e testo nulo

html_tag_type: path del file dei tag html

dipl_inter: d = diplomatica, i=> interpretativa

before_id: prefisso id

__________________________________________________

tx2h.py
  le stesse funzionalità di teixml2html.py senza usare
  il file di configurazione.
    
parametri:

-i file xml 
-o file html
-t fire htmltag.csv
    default: teimcfg/html.csv
-di d)iplomatica i)interpretativa
    default:d
-p  prefisso id
    default K
-wt name_witnesss
    default:witness    
-wa a)append w)write modalità di scrittura output 
    defailt:w
-d  livelo debug 0/1/2
    default:0

Il file di configurazione file.json viene automaticamete creato.
Può essere modificto es usato per lanciare

teixml3html.py
