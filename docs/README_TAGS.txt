========================================
file delle entity HTML
========================================

type|xml_tag|tag|keys|attrs|text|par1ams|par1ent

type selettore della tipologia
  x   per tutti i tipi
  d   diplomatica
  i   interpretativa
  x:txt txt per diplomatica ed interpretativa
  x:syn syn per diplomatica ed interpretativa
  d:txt txt per diplomatica
  i:txt txt per interpretativa
  d:syn syn per diplomatica
  i:syn syn per interpretativa

type|tag|XXX
rimuove il tag

xml_tag
  tag xml per la selezione della riga csv2json

tag
  tag HTML

keys
  elemco keys degli attributi di xml da
  utilizzare nella trasformazione

attrs
  attributi da aggiungere in HTML

text
  testo da aggiungere in HTML

par1ams
  par1ametri nella forma key0:val0, key1:val1, ..
  da utilizzare per settare attrs, text di xml

parent
  utilizza il settore xml del pade quando serve ua
  riferimento ad esso nella peoduzione HTML


testo sul quale si eseguono le sostituzioni
i par1ametri nel testo sono indicati con il pattern
%par1am%

====================================
tag  per il controllo degli erroi nei tag non trovati
====================================
x|x|_x_
x|x+y|_xy_
x|null|null
====================================
tag XML da non trasferire in HTML
====================================
x|tei|XXX|
x|body|XXX|
x|back|XXX|
====================================
text da eliminare da HTML nella ostituzione finale paramtri
====================================
type|xml_tag|tag|keys|attrs|text_null
====================================
<placeName>
contiene sempre <name> (da mettere in maiuscolo)
ed ha l'attributo @type
nel mio caso è stato specificato type="region", type="city", type="castel"
ma il valore dell'attributo non influisce sul comportamento delle maiuscole

<placeName type="region" ref="#$">
     <name><w>$</w></name>
</placeName>
=====================================
<geogName>
contiene sempre <name> (da mettere in maiuscolo)
può contenere <geogFeat> (NON va in maiuscolo)
può avere l'attributo @type, finora non l'ho usato ma è abbastanza comune che ci sia, quindi va previsto. come nel caso di placeName comunque il valore dell'attributo non influisce sul trattamento delle maiuscole

<geogName ref="#$">
    <name><w>$</w></name>
</geogName>

<geogName ref="#$">
     <geogFeat><w>$</w></geogFeat>
     <w>$</w>
    <name><w>$</w></name>
</geogName>
=========================================
