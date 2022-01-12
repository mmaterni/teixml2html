#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace

import argparse
import os
from io import StringIO
import pprint
import re
import sys
import traceback
from lxml import etree
from teimedlib.htmlbuilder import HtmlBuilder
from teimedlib.htmloverflow import HtmlOvweflow
from teimedlib.readhtmlconf import read_html_tag
from teimedlib.readjson import read_json
from teimedlib.uainput import Inp
from teimedlib.ualog import Log
from teimedlib import file_utils as fu

__date__ = "11-01-2022"
__version__ = "0.0.2"
__author__ = "Marta Materni"


def pp(data, w=40):
    s = pprint.pformat(data, indent=2, width=120)
    return s+os.linesep


log_conf = Log("w")
log = Log("a")
log_err = Log("a")
log_csv_err = Log('a')
log_html_err = Log('a')
log_debug = Log('a')

inp = Inp()


def ppx(xdata):
    d = {}
    for k in xdata.keys():
        if k == 'val':
            continue
        d[k] = xdata[k]
    return pp(d)


class Xml2Html:

    def __init__(self):
        log_conf.open("log/teimcfg.json", 0)
        log.open("log/teixml2html.log", 0)
        log_err.open("log/teixml2html.ERR.log", 1)
        log_csv_err.open("log/teixml2html.csv.ERR.log", 1)
        log_html_err.open("log/teixml2html.html.ERR.log", 1)
        log_debug.open("log/DEBUG.log", -1)

        self.xml_path = None
        self.html_path = None
        self.html_teimcfg = None
        self.html_tag_teimcfg = None
        # diplomatica / interpretatova (d/i)
        self.dipl_inter = None
        # prefisso di id per diplomarica / interpretativa
        self.before_id = None
        # HtmlBuilder
        self.hb = None
        # lista x_data (dati xml)
        self.x_data_lst = None
        # dizionario di x_data (dati xml)
        self.x_data_dict = None
        # stack dei valori v/f dei container
        self.is_container_stack = None
        # tag di controllo per erroi csv _x_ _xy_
        self.csv_tag_ctrl = None
        # flag attivo dopo un .,?,!
        self.pc_active = False
        self.w_liv = 0
        # flag per gestione set_trace()
        self.trace = False

    def node_liv(self, node):
        d = 0
        while node is not None:
            d += 1
            node = node.getparent()
        return d - 1

    def clean_key(self, k):
        s = k
        p0 = k.find("{http")
        if (p0 > -1):
            p1 = k.rfind('}')
            if p1 > -1:
                s = k[p1+1:]
        return s

    def node_items(self, nd):
        kvs = nd.items()
        js = {}
        for kv in kvs:
            k = self.clean_key(kv[0])
            v = kv[1]
            js[k] = v
        return js

    def node_tag(self, nd):
        try:
            tag = nd.tag
            tag = tag if type(nd.tag) is str else "XXX"
            pid = tag.find('}')
            if pid > 0:
                tag = tag[pid + 1:]
            return tag.strip()
        except Exception as e:
            log_err.log("ERROR node_tag() ")
            log_err.log(str(e))
            return "XXX"

    def node_id(self, nd):
        s = ''
        kvs = nd.items()
        for kv in kvs:
            if kv[0].rfind('id') > -1:
                s = kv[1]
                break
        return s

    def node_id_num(self, id):
        if id == '':
            return ''
        m = re.search(r'\d', id)
        if m is None:
            return -1
        p = m.start()
        return id[p:]

    def node_text(self, nd):
        text = nd.text
        text = '' if text is None else text.strip()
        text = text.strip().replace(os.linesep, ',,')
        return text

    def node_tail(self, nd):
        tail = '' if nd.tail is None else nd.tail
        tail = tail.strip().replace(os.linesep, '')
        return tail

    def node_val(self, nd):
        ls = []
        for x in nd.itertext():
            s = x.strip().replace(os.linesep, '')
            ls.append(s)
        texts = ' '.join(ls)
        s = re.sub(r"\s{2,}", ' ', texts)
        return s

    def node_is_parent(self, nd):
        cs = nd.getchildren()
        le = len(cs)
        return le > 0

    def get_node_data(self, nd):
        items = self.node_items(nd)
        id = self.node_id(nd)
        if id != '':
            id_num = self.node_id_num(id)
            items['id_num'] = id_num
        return {
            'id': id,
            'liv': self.node_liv(nd),
            'tag': self.node_tag(nd),
            'text': self.node_text(nd),
            'tail': self.node_tail(nd),
            'items': items,
            # 'keys': self.node_keys(nd),
            'val': self.node_val(nd),
            'is_parent': self.node_is_parent(nd)
        }

    def set_text_xitems(self, text, xitems):
        """setta un testo parametrizzato con pars:
        i parametri del testo sono nella forma
        %param% nel cso di parametri riferiti a xsata
        %tag_paren@ù+param% nei parametri che si riferisocono
        ad un tag parent
        NB.
        I parametri  non settati restano nella forma originale
        Args:
            text ([str]): [testo parametrizzato]
            pars ([dict]): [parametri]
        Raises:
            Exception: [tag parent non troaton]
        Returns:
            [str]: [testo parametrizzato settato]
        """
        log_debug.log('**  set_text_xitems')
        log_debug.log(str(xitems))
        log_debug.log(text)
        ptrn = r"%[\w/@,;:.?!-]+%"
        ms = re.findall(ptrn, text)
        ks = [x.replace('%', '') for x in ms]
        try:
            for k in ks:
                if k.find('@') > -1:
                    pk = k.split('@')
                    tag_p = pk[0]
                    k_p = pk[1]
                    x_data_p = self.x_data_dict.get(tag_p, None)
                    if x_data_p is None:
                        raise Exception(f"tag parent {tag_p} not found.")
                    xitems_p = x_data_p['items']
                    v = xitems_p.get(k_p, f'%{k}%')
                else:
                    v = xitems.get(k, f'%{k}%')
                # elimina # dagli items
                v = v.replace('#', '')
                text = text.replace(f'%{k}%', v)
            log_debug.log(text)
            log_debug.log("")
        except Exception as e:
            log_csv_err.log(f"ERROR set_text_xitems()")
            log_csv_err.log(e)
            log_csv_err.log("text: {text}")
            log_csv_err.log("params:", pp(xitems))
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("!")
        return text

    def set_text_parans(self, text, pars):
        """settta pars su text
        vengono consiserati tutti gli elemnti di text dell
        pattern [%][w.?!+][%] e sono rimpiazzati utilizando il dict pars
        NB.
        quelli per i quali non vi sono paramteri corrsipondenti
        SONO lasciati nella loro forma original
        Args:
            text (str): testo con parametri da settare
            pars (dict): parametri per settare text
        Returns:
            str: testo formatato
        """
        if pars == {}:
            return text
        log_debug.log('**  set_text_parans')
        log_debug.log(str(pars))
        log_debug.log(text)
        ptrn = r"%[\w/@,;:.?!-]+%"
        ms = re.findall(ptrn, text)
        if ms is None:
            return text
        ks = [x.replace('%', '') for x in ms]
        for k in ks:
            v = pars.get(k, f'%{k}%')
            text = text.replace(f'%{k}%', v)
        log_debug.log(text)
        log_debug.log("")
        return text

    def remove_text_parans_null(self, text):
        """rimuove parametri non settai
        Args:
            texts ([str]): [testo parametrizzato]
        Returns:
            [str]: [testo con parametri rimossi]
        """
        log_debug.log('**  remove_text_parans_null')
        log_debug.log(text)
        ptrn = r"%[\w/@,;:.?!-]+%"
        ms = re.findall(ptrn, text)
        ks = [x.replace('%', '') for x in ms]
        for k in ks:
            text = text.replace(f'%{k}%', '')
        log_debug.log(text)
        log_debug.log("")
        return text

    def class_adjust(self, text):
        log_debug.log('**  class_adjust')
        log_debug.log(text)
        text = text.replace(' "', '"')
        text = text.replace(' _int', '')
        p0 = text.find('class')
        if p0 > -1:
            p1 = text.find('"', p0+5)
            p2 = text.find('"', p1+1)
            s0 = text[:p2]
            s1 = text[p2:]
            # elimina # dagli attr in html
            text = s0.replace('#', '')+s1
        log_debug.log(text)
        log_debug.log("")
        return text

    # TODO  controllare se non può essere semplifictao
    def replace_text(self, text, text_par):
        """sostiyuisce in text i parametyri %par%
        con i corrisponednti parametri definiti in csv
        il simbolo @ serve ad indicare una diversa riga
        da cui predere iil parametro.
        tag@parm indica di prendere dalla riga corrispondente
        a tag il parametro param
        """
        text0 = text
        log_debug.log('**  replace_text')
        log_debug.log(text)
        ptrn = r"%[\w/@,;:.-]*text%"
        ms = re.findall(ptrn, text)
        ks = [x.replace('%', '') for x in ms]
        ok = False
        try:
            for k in ks:
                if k.find('@') > -1:
                    pk = k.split('@')
                    tag_p = pk[0]
                    x_data_p = self.x_data_dict.get(tag_p, None)
                    if x_data_p is None:
                        raise Exception(
                            f"replace_text tag parent {tag_p} not found.")
                    text_par = x_data_p['text']
                    ok = True
                t0 = text
                text = text.replace(f'%{k}%', text_par)
                if t0 != text:
                    ok = True
        except Exception as e:
            log_csv_err.log(f"ERROR  replace_text()")
            log_csv_err(e)
            log_csv_err.log("text: {text}")
            log_csv_err.log("text_par:", text_par)
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("!")
        # if ok:
        #     print(f"text_orig: {text0}")
        #     print(f"text_par:{text_par}")
        #     print(f"text     :{text}")
        #     set_trace()

        log_debug.log(text)
        log_debug.log(ok)
        log_debug.log("")
        return text, ok

    def attrs2html(self, attrs):
        """trasforma in tag htnl attrs
            ordina partendo da class, id se esistono
        Args:
            attrs (dict): attrs di html
        Returns:
            str: attrs htnl
        """
        ks = []
        if 'class' in attrs.keys():
            ks.append('class')
        if 'id' in attrs.keys():
            ks.append('id')
        for k in attrs.keys():
            if k not in ['id', 'class']:
                ks.append(k)
        ls = []
        for k in ks:
            v = attrs[k]
            if k == 'id':
                v = f'{self.before_id}{v}'
            s = f'{k}="{v}"'
            ls.append(s)
        return " ".join(ls)

    def html_attrs_builder(self, x_items, c_keys=[], c_attrs={}):
        """seleziona gli elemnti di x_items filtrati da c_kets
           aggiunge gli elementi c_attrs {}
        Args:
            x_items ([dict]): xml items
            c_keys (dict, optional): keys seleziona fi element di x_items
            c_attrs (dict, optional): csv attr
        Returns:
            attrs (dict): dict unione dei parametri e degli items del parent
       """
        attrs = {}
        for k in c_keys:
            if k in x_items:
                attrs[k] = x_items[k]
        for k in c_attrs.keys():
            attrs[k] = c_attrs[k]
        html_attrs = self.attrs2html(attrs)
        return html_attrs

    def get_data_row_html_csv(self, x_data):
        """ ritorna dati della row di <tag>.csv individuata
            dall tag o tag+attr di x_data del in xml_data_dict
            la key è quella ottenuta dal tag xml 
            e l'eventuale/i attributo
        Args:
            x_data (dict):xml data
        Returns:
            [row_data (dict): dati estartti da csv
        """
        xml_tag = x_data['tag']
        row_data = self.html_tag_teimcfg.get(xml_tag, None)
        if row_data is None:
            row_data = self.html_tag_teimcfg.get('x', {})
            csv_tag = xml_tag
            self.csv_tag_ctrl = f'_x_{csv_tag}'
        else:
            tag = row_data.get('tag', f"_x_{xml_tag}")
            p = tag.find('+')
            if p > -1:
                x_items = x_data['items']
                # tag|tag + att1_name + attr2_name+..
                # x_items[attr<n>_name]  => [attr1_val,attr2_val]
                # #tag + attr1_val + att2_vap + ..
                lsk = tag.split('+')[1:]
                lsv = [x_items[k] for k in lsk if k in x_items.keys()]
                attrs_val = '+'.join(lsv)
                csv_tag = xml_tag+'+'+attrs_val
                row_data = self.html_tag_teimcfg.get(csv_tag, None)
                if row_data is None:
                    row_data = self.html_tag_teimcfg.get('x+y', None)
                    self.csv_tag_ctrl = f'_xy_{csv_tag}'
                else:
                    self.csv_tag_ctrl = csv_tag
            else:
                csv_tag = xml_tag
                self.csv_tag_ctrl = csv_tag
        # nel test non si è mai verificato
        if self.csv_tag_ctrl != csv_tag:
            log_csv_err.log("ERROR get_data_row_html_csv()")
            log_csv_err.log(f"xml_tag: {xml_tag}")
            log_csv_err.log(f"csv_tag: {csv_tag}")
            log_csv_err.log(f"csv_tag_ctrl: {self.csv_tag_ctrl}")
            log_csv_err.log(ppx(x_data)).prn()
            inp.inp("!")
        self.x_data_dict[csv_tag] = x_data
        return row_data

    def get_tag_w_last(self):
        """ 
        ultimo tag con id  significativo
        correttamnte utilizzato.
        In caso di errore + l'ultimo tag corretto
        """
        tag_w_last = ''
        le = len(self.hb.get_tag_lst())
        if le == 0:
            return ""
        x = 5 if le > 5 else le
        for i in range(1, x):
            tag_w_last = self.hb.get_tag_lst()[-i:][0].strip()
            if tag_w_last.find('id') > -1:
                break
        return tag_w_last

    def build_html_data(self, x_data):
        """raccoglie i dati per costruire un elemnt html
        Args:
            x_data (dict): dati presi da xml
        Returns:
            dict: dati necessari a costruire html
        """
        x_items = x_data['items']
        x_text = x_data['text']
        x_tail = x_data['tail']
        x_liv = x_data['liv']
        self.is_container_stack[x_liv] = False
        c_data = self. get_data_row_html_csv(x_data)
        ################################
        if inp.prn:
            log.log("============").prn()
            log.log(">> x_data").prn()
            log.log(ppx(x_data)).prn()
            log.log(">> csv_data").prn()
            log.log(pp(c_data)).prn()
            log.log("============").prn()
        ################################
        c_tag = c_data.get('tag')
        # c_keys sone le key degli elementi di items da prendere
        c_keys = c_data.get('keys', [])
        c_attrs = c_data.get('attrs', {})
        c_text = c_data.get('text', "")
        c_params = c_data.get('params', {})
        #
        # unisce x_items selezionato da c_keys + c_attrs
        html_attrs = self.html_attrs_builder(x_items, c_keys, c_attrs)
        log_debug.log(
            f".0 -------- {x_data['tag']}  {x_data['liv']} ---------")
        log_debug.log(str(x_data))
        log_debug.log(str(c_data))

        if html_attrs.find('%') > -1:
            log_debug.log(".1 attrs")
            # rimpiazza se esiste %text% con x_data['text']
            html_attrs, is_replace = self.replace_text(html_attrs, x_text)
            # setta parametri utilizzando c_params
            html_attrs = self.set_text_parans(html_attrs, c_params)
            html_attrs = self.set_text_xitems(html_attrs, x_items)
            html_attrs = self.remove_text_parans_null(html_attrs)
            html_attrs = self.class_adjust(html_attrs)

        # setta c_text itilizzando ext_items :items + parent.items)
        if c_text.find('%') > -1:
            log_debug.log(".2 c_text")
            c_text = self.set_text_parans(c_text, c_params)
            c_text = self.set_text_xitems(c_text, x_items)

            # quando in c_data tetx=%%text%% il text di x_data
            # sostituisce %text$ . Es:
            # x_data x_text='c' ==>  in c_data c_text=%c$
            # se la sostituzione avviene viene posto x_text=''
            log_debug.log(".3 c_text")
            c_text, is_replace = self.replace_text(c_text, x_text)
            if is_replace:
                x_text = ''

            # setta c_text utilizzando c_params
            log_debug.log(".4 c_text")
            c_text = self.set_text_parans(c_text, c_params)

        log_debug.log(".5")
        log_debug.log(x_text+c_text+x_tail)
        log_debug.log(html_attrs)
        #
        html_text = x_text+c_text
        ####################
        html_data = {
            'tag': c_tag,
            'attrs': html_attrs,
            'text': html_text,
            'tail': x_tail
        }
        # ERRORi nella gestione del files csv dei tag html
        if self.csv_tag_ctrl.find('_x') > -1:
            log_csv_err.log("ERROR build_html_data()")
            log_csv_err.log(f"in csv tag:{self.csv_tag_ctrl}")
            log_csv_err.log(f"file: {self.xml_path}")
            log_csv_err.log("xml:", ppx(x_data))
            log_csv_err.log("xml:", ppx(x_data))
            log_csv_err.log("csv:", self.csv_tag_ctrl)
            log_csv_err.log("html:", pp(html_data))
            # ultimo tag w prima dell'ERRORe
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("!")
        ################################
        if inp.prn:
            log.log(">> html_data").prn()
            log.log(pp(html_data)).prn()
        ################################
        #  valutare se exit/1) al verificarsi dell'errore
        # sys.exit(1)
        return html_data

    def set_pc(self, x_data):
        x_tag = x_data['tag']
        if self.w_liv == 0 and x_tag == 'w':
            self.w_liv = x_data['liv']
        if x_tag == 'pc':
            t = x_data['text'].strip()
            if t in ['.', '?', '!']:
                self.pc_active = True

    def after_pc(self, x_data, h_data, text, tail):
        x_liv = x_data['liv']
        x_tag = x_data['tag']
        if x_tag == 'w':
            self.w_liv = x_liv
            if text.strip() != '':
                # text='X'+text
                text = text.capitalize()
                self.pc_active = False
                self.w_liv = 100
        h_tag = h_data['tag']
        if x_liv > self.w_liv and h_tag != 'XXX':
            if text.strip() != '':
                # text='X'+text
                text = text.capitalize()
                self.pc_active = False
                self.w_liv = 100
            elif tail.strip() != '':
                tail = 'Y'+tail
                # tail=tail.capitalize()
                self.pc_active = False
                self.w_liv = 100
        return text, tail

    def apped_html_data(self, nd):
        """
        estrae da nd x_data
        invoca build_html_data()
        setta:h_data
        utilizza self.hb (HtmlBuildr) per costruire HTML
        popola self.hb
        Args:
            nd (xml.node): nodo xml
        """
        x_data = self.get_node_data(nd)
        # UA
        # if self.dipl_inter == 'i':
        #     if x_data['id'] == "Gl14w1":
        #         # self.trace=True
        #         # inp.set_liv(2)
        #         # log_debug.set_liv(1)
        #         # set_trace()
        #         pass
        # else:
        #     # log_debug.set_liv(0)
        #     pass
        ##########################
        # aggiorna xml_data_lst da utilzzare per HtmlOverflow
        self.x_data_lst.append(x_data)
        x_liv = x_data['liv']
        x_is_parent = x_data['is_parent']
        x_tag = x_data['tag']
        # setta dati per tag html
        h_data = self.build_html_data(x_data)
        h_tag = h_data['tag']
        h_text = h_data['text']
        h_tail = h_data['tail']
        h_attrs = h_data['attrs']
        # se il precedente è un parent contenitor
        prev_is_container = self.is_container_stack[x_liv-1]
        if prev_is_container:
            # TODO verificare gestione container
            # set_trace()
            # rimpiazza text  nel tag precdente (il container)
            content = f'<{h_tag} {h_attrs}>{h_text}</{h_tag}>{h_tail}'
            s = self.hb.tag_last()
            content = s.replace('%text%', content)
            self.hb.upd_tag_last(content)
            # setta con XXX perrimuovere da aggiungere in quanto
            # è stato inserito nel contente del parent
            h_tag = 'XXX'
        # gestione interpretativa
        if self.dipl_inter == 'i':
            h_text = h_text.lower()
            h_tail = h_tail.lower()
            self.set_pc(x_data)
            if self.pc_active:
                h_text, h_tail = self.after_pc(x_data, h_data, h_text, h_tail)
        # popola self.hb
        if x_is_parent:
            self.hb.opn(x_liv, h_tag, h_attrs, h_text, h_tail)
        else:
            self.hb.ovc(x_liv, h_tag, h_attrs, h_text, h_tail)
        #######################
        l = self.hb.tag_last()
        log_debug.log(l)
        #####################
        if inp.prn:
            log.log(">> html node").prn()
            log.log(self.hb.tag_last()).prn()
        inp.inp(x_tag)
        if inp.equals('?'):
            print(self.hb.html_format())
            inp.inp()

    def set_html_pramas(self, html):
        """utilizzando il file json formatta i parametri residui
            es. il nome del manoscrittp _MAN_
            qualsiasi altro parametro definito nel file cid configurazione
            al tag html_params
        Args:
            html (str): html 
        Returns:
            html (str): html con settati i parametri         """
        params = self.html_teimcfg.get("html_params", {})
        for k, v in params.items():
            html = html.replace(k, v)
        return html

    def check_tml(self):
        """ controlla tutte le righe htnl di HtmlBuilder
        per verificare che vi sda qualche parametro
        del tipo %param% non settato
        """
        ptrn = r"%[\w/,;:.?!^-]+%"
        rows = self.hb.get_tag_lst()
        le = len(rows)
        for i, row in enumerate(rows):
            ms = re.search(ptrn, row)
            if ms is not None:
                log_html_err.log("ERROR check_tml()")
                log_html_err.log(f"parametro: {ms.group()}")
                log_html_err.log(f"file: {self.xml_path}")
                if i > 3:
                    log_html_err.log(rows[i-3].strip())
                if i > 2:
                    log_html_err.log(rows[i-2].strip())
                if i > 1:
                    log_html_err.log(rows[i-1].strip())
                log_html_err.log("**")
                log_html_err.log("     "+row.strip())
                log_html_err.log("**")
                if i < le-2:
                    log_html_err.log(rows[i+1].strip())
                if i < le-3:
                    log_html_err.log(rows[i+2].strip())
                if i < le-4:
                    log_html_err.log(rows[i+3].strip())
                # tag_w_last = self.get_tag_w_last()
                # log_html_err.log("last w: ", tag_w_last)
                log_html_err.log(os.linesep)
                inp.inp('!')
                #  valutare se exit/1) al verificarsi dell'errore
                # sys.exit(1)

    def default_conf(self, wtn, di):
        self.html_teimcfg = {
            "html_params": {
                "_MAN_": wtn,
                "text_null": "",
                "_QA_": "\"",
                "_QC_": "\""
            },
            "html_tag_file": "teimcfg/html.csv",
            "html_tag_type": di+":txt",
            "dipl_inter": di,
            "before_id": di
        }
        try:
            log_conf.log(pp(self.html_teimcfg).replace("'", '"')).prn(0)
            #
            # hrml dipl./inter
            self.dipl_inter = self.html_teimcfg.get("dipl_inter", None)
            if self.dipl_inter is None or self.dipl_inter not in ['d', 'i']:
                raise Exception(f"ERROR dipl_inter: {self.dipl_inter}")
            #
            # prefisso di id per diplomatia e interpretativa
            self.before_id = self.html_teimcfg.get("before_id", None)
            if self.before_id is None:
                raise Exception("ERROR before_id is null.")
            #
            csv_path = self.html_teimcfg.get("html_tag_file", None)
            if csv_path is None:
                raise Exception("ERROR html_tag_file is null.")
            #
            # type : d:txt d:syn i:txt i:syn
            html_tag_type = self.html_teimcfg.get("html_tag_type", None)
            if html_tag_type is None:
                raise Exception("ERROR html_tag_type is null.")
            self.html_tag_teimcfg = read_html_tag(csv_path, html_tag_type)
            log_conf.log(pp(self.html_tag_teimcfg).replace("'", '"')).prn(0)
        except Exception as e:
            log_err.log("ERROR: default_conf()")
            log_err.log(e)
            sys.exit(1)

    def read_conf(self, json_path):
        try:
            self.html_teimcfg = read_json(json_path)
            log_conf.log(pp(self.html_teimcfg).replace("'", '"')).prn(0)
            #
            # hrml dipl./inter
            self.dipl_inter = self.html_teimcfg.get("dipl_inter", None)
            if self.dipl_inter is None or self.dipl_inter not in ['d', 'i']:
                raise Exception(f"ERROR dipl_inter: {self.dipl_inter}")
            #
            # prefisso di id per diplomatia e interpretativa
            self.before_id = self.html_teimcfg.get("before_id", None)
            if self.before_id is None:
                raise Exception("ERROR before_id is null.")
            #
            csv_path = self.html_teimcfg.get("html_tag_file", None)
            if csv_path is None:
                raise Exception("ERROR html_tag_file is null.")
            #
            # type : d:txt d:syn i:txt i:syn
            html_tag_type = self.html_teimcfg.get("html_tag_type", None)
            if html_tag_type is None:
                raise Exception("ERROR html_tag_type is null.")
            self.html_tag_teimcfg = read_html_tag(csv_path, html_tag_type)
            log_conf.log(pp(self.html_tag_teimcfg).replace("'", '"')).prn(0)
        except Exception as e:
            log_err.log("ERROR: read_conf())")
            log_err.log(e)
            sys.exit(1)

    def write_html(self,
                   xml_path,
                   html_path,
                   conf_path,
                   wtn,
                   dipint,
                   write_append='w',
                   debug_liv=0):
        """fa il parse del file xml_path scrive i files:
            nel formato comapatto: <html_path>
            formato indentato <html_name>_f.html
        Args:
            xml_path (str]:  file xml
            html_path (str): file html
            conf_path (str): file di configurazoine
            write_append(str): modalità output
            deb (bool, optional): flag per gestione debug
            wtn:noeme witnes alternativo a json_path
            dipint:dipl/intr alternaivo a json_pat
        Returns:
            html_path (str): filr name html 
        """
        try:
            inp.set_liv(debug_liv)
            self.x_data_lst = []
            self.xml_path = xml_path
            self.html_path = html_path
            if write_append not in ['w', 'a']:
                raise Exception(
                    f"ERROR in output write/append. {write_append}")
            try:
                # lettura file configurazione
                if len(conf_path) > 1:
                    self.read_conf(conf_path)
                elif len(wtn) > 1 and len(dipint) > 0:
                    self.default_conf(wtn, dipint)
                else:
                    raise Exception(
                        "ERROR teixml2html.py write_html() config is null")
            except Exception as e:
                log_err.log("ERROR write_html() 1")
                log_err.log(e)
                sys.exit(1)
            # lib per costruziona html
            # TODO verificare se non settarlo all'inizio
            self.hb = HtmlBuilder()
            # dict dei dati xml con tag come key
            self.x_data_dict = {}
            # stack dei nodi che sono si/no container
            self.is_container_stack = [False for i in range(1, 20)]
            # tag per controlo ERRORi
            self.csv_tag_ctrl = ""
            #
            self.hb.init()
            try:
                # parser = etree.XMLParser(remove_blank_text=True)
                # xml_root = etree.parse(self.xml_path, parser)
                src = open(self.xml_path, "r").read()
                src = src.replace("<TEI>", "")
                src = src.replace("</TEI>", "")
                # TODO da verificare l'aggiunta di <div>
                src = "<div>"+src+"</div>"
                parser = etree.XMLParser(ns_clean=True)
                xml_root = etree.XML(src, parser)
            except Exception as e:
                log_err.log("ERROR write_html() 2")
                log_err.log(e)
                sys.exit(1)
            #########################
            for nd in xml_root.iter():
                self.apped_html_data(nd)
            #########################
            self.hb.del_tags('XXX')
            self.hb.end()
            """gestisce il settaggio degli overflow
            modifica il parametro html_lst
            e quindi hb.html_lst  
            #TODO  forse si puo passare direttamente hb.tml_lst
           """
            html_lst = self.hb.get_tag_lst()
            html_over = HtmlOvweflow(self.x_data_lst,
                                     html_lst,
                                     self.html_tag_teimcfg)
            html_over.set_overflow()
            # controllo dei parametri %par% non settati
            self.check_tml()
            # html su una riga versione per produzione
            html = self.hb.html_onerow()
            html = self.set_html_pramas(html)
            fu.make_dir_of_file(self.html_path)
            with open(self.html_path, write_append) as f:
                f.write(html)
            fu.chmod(self.html_path)
        except Exception as e:
            log_err.log("ERROR write_html() 3")
            log_err.log(e)
            #
            ou = StringIO()
            traceback.print_exc(file=ou)
            st = ou.getvalue()
            ou.close()
            log_err.log(st)
            sys.exit(1)
        return self.html_path


def do_mauin(xml, html, conf_path, wtn, dipint, wa='w', deb=False):
    Xml2Html().write_html(xml, html, conf_path, wtn, dipint, wa, deb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-d',
                        dest="deb",
                        required=False,
                        metavar="",
                        default=0,
                        help="[-d 0/1/2](setta livello di debug)")
    parser.add_argument('-wa',
                        dest="wa",
                        required=False,
                        metavar="",
                        default="w",
                        help="[-wa w/a (w)rite a)ppend) default w")

    parser.add_argument('-c',
                        dest="confpath",
                        required=False,
                        default="",
                        metavar="",
                        help="-c <file_conf.json")
    parser.add_argument('-wt',
                        dest="wtn",
                        required=False,
                        default="",
                        metavar="",
                        help="-w <witness>")
    parser.add_argument('-di',
                        dest="dipint",
                        required=False,
                        default="",
                        metavar="d)iplomat/i)terpret",
                        help="-di <d/i>")

    parser.add_argument('-i',
                        dest="xml",
                        required=True,
                        metavar="",
                        help="-i <file_in.xml>")
    parser.add_argument('-o',
                        dest="html",
                        required=True,
                        metavar="",
                        help="-o <file_out.html>")
    args = parser.parse_args()
    do_mauin(args.xml,
             args.html,
             args.confpath,
             args.wtn,
             args.dipint,
             args.wa,
             args.deb)
