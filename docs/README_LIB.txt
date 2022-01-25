teixml2html.py
    trasforma file xm in file html utilizzando un file di
    csv dve sono definiti le entity per l trasformazione

lancio con file di configurazione:

teixmltohtml.py -i file.xml -o file.html -c file_config.json [-wa a/w] [-d 1/2/3]

lancio con parametri;

teixmltohtml.py -i file.xml -o file.html -wt witness - di /d/i  [-wa a/w] [-d 1/2/3]






=====================================================
librerie:
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

copy2all.py
  copia i file json di un manoscritto in quelli di n 
  manoscriiti

htmlformat.py
    formatta i file htmlformat
    
prjmgr.py
    gestisce progetti definiti in file json

splitteixml.py
  separa iun file xml di un manoscritto nei file xml dei
  vari capitoli/eoisodi

uainput.py
    utiliti per il debug di teimed3html

ualog.py
    gestione dei log
