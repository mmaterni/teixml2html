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

teixml2html.py

=====================================================
librerie ed uitlity per gestione project
=====================================================

    htmlbuilder.py
        costruisce nodo per nodo un file HTML

    htmloverflow.py
         gestisce gli overflow tei DEI FILE XML:
         discorso diretto, monologo, parole danneggiate
    
    readhtmlconf.py
        legge il file dele enntitiy htmltag.csv e tarsgorma
        i dati in un dictionary

    readjson.py
        legge i file json e restitusice un dictionary

writehtmlfile.py
     [-d 0/1/2](setta livello di debug)")
     [-wa w/a (w)rite a)ppend) default w")
     -c <file_conf.json")
     -i <file_in.xml>")
     -o <file_out.html>")

    copia un  file template html all'interno di un progetto
    gestito da prjmgr.py

writehtml.py
    copia un template html all'interno di un progetto
    gestitpo da prjmgr.py

htmlformat.py
    formatta i file htmlformat
    
prjmgr.py
    gestisce progetti definiti in file json

splitteixml.py
  separa iun file xml di un manoscritto nei file xml dei
  vari capitoli/eoisodi

uainput.py
    utilitwy per il debug di teimed3html

ualog.py
    gestione dei log

