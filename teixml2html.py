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
#from lxml import etree
from teimedlib.htmlbuilder import HtmlBuilder
from teimedlib.htmloverflow import HtmlOvweflow
from teimedlib.readhtmlconf import read_csv
from teimedlib.readjson import read_json
from teimedlib.uainput import Inp
from teimedlib.ualog import Log
from teimedlib import file_utils as fu
#from teiprjhtmlmake import LOG
from teimedlib.xml_node_list import XmlNodeList


__date__ = "23-01-2022"
__version__ = "0.0.5"
__author__ = "Marta Materni"

DEBUG_HTML = False
LOG_ERR_WA = 'a'


log_conf = Log("w")
log_info = Log("w")
log_err = Log(LOG_ERR_WA)
log_csv_err = Log(LOG_ERR_WA)
log_html_err = Log(LOG_ERR_WA)
log_debug = Log("a")

inp = Inp()

def pp(data, w=120):
    s = pprint.pformat(data, indent=2, width=w)
    return s

def ppx(xdata, w=120):
    d = {}
    for k in xdata.keys():
        if k == 'val':
            continue
        d[k] = xdata[k]
    return pp(d, w)

class Xml2Html:

    def __init__(self):
        log_info.open("log/teixml2html.log", 0)
        log_conf.open("log/teimcfg.json", 0)
        log_err.open("log/teixml2html.ERR.log", 1)
        log_csv_err.open("log/teixml2html.csv.ERR.log", 1)
        log_html_err.open("log/teixml2html.html.ERR.log", 1)
        log_debug.open("log/DEBUG.log", 1)

        self.xml_path = None
        self.html_path = None
        self.html_cfg = None
        self.html_tag_teimcfg = None

        # diplomatica / interpretatova (d/i)
        self.dipl_inter = None

        # prefisso di id per diplomarica / interpretativa
        self.before_id = None
        self.hb = HtmlBuilder()

        # lista x_data (dati xml)
        self.x_data_lst = None
        
        # dizionario di x_data (dati xml) con key csv
        # utilizzato per trovare il parent come indicato in csv
        # TODO controllare se possibili alternative
        self.x_data_dict = None
        
        # stack dei nodi che sono si/no container
        # BUG verificare funzionamento
        self.is_container_stack = [False for i in range(1, 20)]
        
        # tag di controllo per erroi csv _x_ _xy_
        self.csv_tag_ctrl = None

        self.w_liv = 0
        # flag per gestione set_trace()
        self.trace = False

    # def node_liv(self, node):
    #     d = 0
    #     while node is not None:
    #         d += 1
    #         node = node.getparent()
    #     return d - 1

    # def clean_key(self, k):
    #     s = k
    #     p0 = k.find("{http")
    #     if (p0 > -1):
    #         p1 = k.rfind('}')
    #         if p1 > -1:
    #             s = k[p1+1:]
    #     return s

    # def node_items(self, nd):
    #     kvs = nd.items()
    #     js = {}
    #     for kv in kvs:
    #         k = self.clean_key(kv[0])
    #         v = kv[1]
    #         js[k] = v
    #     return js

    # def node_tag(self, nd):
    #     try:
    #         tag = nd.tag
    #         tag = tag if type(nd.tag) is str else "XXX"
    #         pid = tag.find('}')
    #         if pid > 0:
    #             tag = tag[pid + 1:]
    #         return tag.strip()
    #     except Exception as e:
    #         log_err.log(f"ERROR {self.xml_path} node_tag() ")
    #         log_err.log(e)
    #         return "XXX"

    # def node_id(self, nd):
    #     s = ''
    #     kvs = nd.items()
    #     for kv in kvs:
    #         if kv[0].rfind('id') > -1:
    #             s = kv[1]
    #             break
    #     return s

    # def node_id_num(self, id):
    #     if id == '':
    #         return ''
    #     m = re.search(r'\d', id)
    #     if m is None:
    #         return -1
    #     p = m.start()
    #     return id[p:]

    # def node_text(self, nd):
    #     text = nd.text
    #     text = '' if text is None else text.strip()
    #     text = text.strip().replace(os.linesep, ',,')
    #     return text

    # def node_tail(self, nd):
    #     tail = '' if nd.tail is None else nd.tail
    #     tail = tail.strip().replace(os.linesep, '')
    #     return tail

    # def node_val(self, nd):
    #     ls = []
    #     for x in nd.itertext():
    #         s = x.strip().replace(os.linesep, '')
    #         ls.append(s)
    #     texts = ' '.join(ls)
    #     s = re.sub(r"\s{2,}", ' ', texts)
    #     return s

    # def node_is_parent(self, nd):
    #     cs = nd.getchildren()
    #     le = len(cs)
    #     return le > 0

    # def get_node_data(self, nd):
    #     items = self.node_items(nd)
    #     id = self.node_id(nd)
    #     if id != '':
    #         id_num = self.node_id_num(id)
    #         items['id_num'] = id_num
    #     return {
    #         'id': id,
    #         'liv': self.node_liv(nd),
    #         'tag': self.node_tag(nd),
    #         'text': self.node_text(nd),
    #         'tail': self.node_tail(nd),
    #         'items': items,
    #         # 'keys': self.node_keys(nd),
    #         'val': self.node_val(nd),
    #         'is_parent': self.node_is_parent(nd)
    #     }


    # html_attrs = self.set_x_items(html_attrs, x_items)
    # c_text = self.set_x_items(c_text, x_items)
    def set_x_items(self, src, x_items):
        """setta un testo parametrizzato con x_items:
        i parametri del testo sono nella forma
        %param% nel cso di parametr %tag_paren@ù+param% 
        tag_parent estrae da x_data_dict x_data
        memorizzato con il tag pag_arente e pren x_items
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
        ptrn = r"%[\w/@,;:.?!-]+%"
        ms = re.findall(ptrn, src)
        ks = [x.replace('%', '') for x in ms]
        try:
            for k in ks:
                if k.find('@') > -1:
                    pk = k.split('@')
                    tag_p = pk[0]
                    k_p = pk[1]
                    #UA 
                    x_data_p = self.x_data_dict.get(tag_p, None)
                    # print("------------------------")
                    # print(self.xml_path)
                    # print(src)
                    # print("x_items: "+pp(x_items))
                    # print("ks: "+pp(ks))
                    # print("k: "+k)
                    # print(tag_p)
                    # print(pp(x_data_p))
                    # input("?")
                    if x_data_p is None:
                        raise Exception(f"tag parent {tag_p} not found.")
                    xitems_p = x_data_p['items']
                    v = xitems_p.get(k_p, f'%{k}%')
                else:
                    v = x_items.get(k, f'%{k}%')
                # elimina # dagli items
                v = v.replace('#', '')
                src = src.replace(f'%{k}%', v)
        except Exception as e:
            log_csv_err.log(f"ERROR {self.xml_path}  set_text_xitems()")
            log_csv_err.log(e)
            log_csv_err.log("text: {text}")
            log_csv_err.log("params:", pp(x_items))
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("?", "!")
        return src

    def sett_c_params(self, src, c_params):
        """settta pars su src
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
        if c_params == {}:
            return src
        ptrn = r"%[\w/@,;:.?!-]+%"
        ms = re.findall(ptrn, src)
        if ms is None:
            return src
        ks = [x.replace('%', '') for x in ms]
        for k in ks:
            v = c_params.get(k, f'%{k}%')
            src = src.replace(f'%{k}%', v)
        return src

    def remove_params_null(self, text):
        """rimuove parametri non settai
        Args:
            texts ([str]): [testo parametrizzato]
        Returns:
            [str]: [testo con parametri rimossi]
        """
        ptrn = r"%[\w/@,;:.?!-^]+%"
        ms = re.findall(ptrn, text)
        ks = [x.replace('%', '') for x in ms]
        for k in ks:
            text = text.replace(f'%{k}%', '')
        return text

    def class_adjust(self, text):
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
        return text

    def set_text_in_html_attr(self, html_attrs, x_text):
        """sostuiuisce i parametri %text% in html_attrs
        con x_text estratto da x_data
        il simbolo @ serve ad indicare una diversa riga
        da cui predere il parametro.
        tag@parm indica di prendere dalla riga corrispondente
        a tag il parametro param
        """
        ptrn = r"%[\w/@,;:.-^]*text%"
        ms = re.findall(ptrn, html_attrs)
        ks = [x.replace('%', '') for x in ms]
        try:
            for k in ks:
                # text_par preso da una riga CSV puntata da @
                if k.find('@') > -1:
                    pk = k.split('@')
                    tag_p = pk[0]
                    #UA
                    x_data_p = self.x_data_dict.get(tag_p, None)

                    # print("------------------------")
                    # print(self.xml_path)
                    # print(html_attrs)
                    # print("x_text: "+x_text)
                    # print("ks: "+pp(ks))
                    # print("k: "+k)
                    # print(tag_p)
                    # print(pp(x_data_p))
                    # input("?")

                    if x_data_p is None:
                        raise Exception(
                            f"tag parent:{tag_p} not found.")
                    x_text = x_data_p['text']
                html_attrs = html_attrs.replace(f'%{k}%', x_text)
        except Exception as e:
            log_csv_err.log(f"ERROR {self.xml_path}  set_text_in_html_attr()")
            log_csv_err(e)
            log_csv_err.log("text: {text}")
            log_csv_err.log("text_par:", x_text)
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("?", "!")
        return html_attrs

    def set_text_in_c_text(self, c_text, x_text):
        """sostuiuisce i parametri %text% in c_text
        con x_text estratto da x_data
        il simbolo @ serve ad indicare una diversa riga
        da cui predere il parametro.
        tag@parm indica di prendere dalla riga corrispondente
        a tag il parametro param
        """
        ptrn = r"%[\w/@,;:.-^]*text%"
        ms = re.findall(ptrn, c_text)
        ks = [x.replace('%', '') for x in ms]
        ok = False
        t0 = c_text
        try:
            for k in ks:
                # text_par preso da una riga CSV puntata da @
                if k.find('@') > -1:
                    pk = k.split('@')
                    tag_p = pk[0]
                    #UA
                    x_data_p = self.x_data_dict.get(tag_p, None)

                    # print("------------------------")
                    # print(self.xml_path)
                    # print(c_text)
                    # print("x_text: "+x_text)
                    # print("ks: "+pp(ks))
                    # print("k: "+k)
                    # print(tag_p)
                    # print(pp(x_data_p))
                    # input("?")

                    if x_data_p is None:
                        raise Exception(
                            f"tag parent: {tag_p} not found.")
                    x_text = x_data_p['text']
                    ok = True

                c_text = c_text.replace(f'%{k}%', x_text)
            if t0 != c_text:
                ok = True
        except Exception as e:
            log_csv_err.log(f"ERROR {self.xml_path} set_text_in_c_text()")
            log_csv_err(e)
            log_csv_err.log("text: {text}")
            log_csv_err.log("text_par:", x_text)
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("?", "!")
        return c_text, ok

    def attrs2html(self, attrs):
        """trasforma in tag htnl attrs
            ordina partendo da class,id se esistono
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

    def build_html_attrs(self, x_items, c_keys=[], c_attrs={}):
        """seleziona gli elemnti di x_items filtrati da c_kets
           aggiunge gli elementi c_attrs {}
        Args:
            x_items ([dict]): xml items
            c_keys (dict, optional): keys seleziona fi element di x_items
            c_attrs (dict, optional): csv attrs
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

            se per xml_tag row_data is None
              csv_tag_ctrl="_x_"+csv_tag
              csv_tag=xml_tag
           se xml_tag è complessa (tag + attrs) e tag is None
              csv_tag_ctrl="_xy_"+csv_tag
        Args:
            x_data (dict):xml data
        Returns:
            [c_data (dict): dati estartti da csv
            setta x_data_dict
        """
        xml_tag = x_data['tag']
        c_data = self.html_tag_teimcfg.get(xml_tag, None)
        if c_data is None:
            c_data = self.html_tag_teimcfg.get('x', {})
            csv_tag = xml_tag
            self.csv_tag_ctrl = f'_x_{csv_tag}'
        else:
            tag = c_data.get('tag', f"_x_{xml_tag}")
            p = tag.find('+')
            if p > -1:
                # tag + attrs
                x_items = x_data['items']
                # tag|tag + att1_name + attr2_name+..
                # x_items[attr<n>_name]  => [attr1_val,attr2_val]
                # tag + attr1_val + att2_val + ..
                lsk = tag.split('+')[1:]
                lsv = [x_items[k] for k in lsk if k in x_items.keys()]
                attrs_val = '+'.join(lsv)
                csv_tag = xml_tag+'+'+attrs_val
                c_data = self.html_tag_teimcfg.get(csv_tag, None)
                if c_data is None:
                    c_data = self.html_tag_teimcfg.get('x+y', None)
                    self.csv_tag_ctrl = f'_xy_{csv_tag}'
                else:
                    self.csv_tag_ctrl = csv_tag
            else:
                # tag semplice
                csv_tag = xml_tag
                self.csv_tag_ctrl = csv_tag
        # csv_tag_ctrl = csv_tag se row_data trovato
        if self.csv_tag_ctrl != csv_tag:
            log_csv_err.log(f"ERROR {self.xml_path}  get_data_row_html_csv()")
            log_csv_err.log(f"xml_tag: {xml_tag}")
            log_csv_err.log(f"csv_tag: {csv_tag}")
            log_csv_err.log(f"csv_tag_ctrl: {self.csv_tag_ctrl}")
            log_csv_err.log(ppx(x_data))
            inp.inp("?", "!")
            c_data = {}
            # sys.exit(1)
        #BUG  popola il dict utilizzando csv_tag come chiave
        self.x_data_dict[csv_tag] = x_data
        return c_data

    def get_tag_w_last(self):
        """
        ultimo tag con id significativo
        correttamnte utilizzato.
        In caso di errore + l'ultimo tag corretto
        """
        tag_w_last = ''
        le = len(self.hb.tag_lst)
        if le == 0:
            return ""
        x = 5 if le > 5 else le
        for i in range(1, x):
            tag_w_last = self.hb.tag_lst[-i:][0].strip()
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
        x_tag = x_data['tag']
        x_items = x_data['items']
        x_text = x_data['text']
        x_tail = x_data['tail']
        x_liv = x_data['liv']

        # TODO verificare quando è settato container
        self.is_container_stack[x_liv] = False

        c_data = self. get_data_row_html_csv(x_data)
        c_tag = c_data.get('tag')
        # c_keys sone le key degli elementi di items da prendere
        c_keys = c_data.get('keys', [])
        c_attrs = c_data.get('attrs', {})
        c_text = c_data.get('text', "")
        c_params = c_data.get('params', {})

        # x_items selezionati da c_keys + c_attrs
        html_attrs = self.build_html_attrs(x_items, c_keys, c_attrs)

        log_info.log("---------------------------").prn(0)
        log_info.log(f"TAG: {x_tag}  {c_tag}").prn(0)
        log_info.log(">> x_data").prn(0)
        log_info.log(ppx(x_data)).prn(0)
        log_info.log(">> c_data").prn(0)
        log_info.log(pp(c_data)).prn(0)
        log_info.log(">>1) html_attrs").prn(0)
        log_info.log(html_attrs).prn(0)

        # sostituzioni
        if html_attrs.find('%') > -1:
            # sostituisce %text% con x_data['text']
            html_attrs = self.set_text_in_html_attr(html_attrs, x_text)
            # setta parametri utilizzando c_params
            html_attrs = self.sett_c_params(html_attrs, c_params)
            # setta parametri utilizzando x_items
            html_attrs = self.set_x_items(html_attrs, x_items)
            html_attrs = self.remove_params_null(html_attrs)
            html_attrs = self.class_adjust(html_attrs)

        # setta c_text itilizzando ext_items :items + parent.items)
        if c_text.find('%') > -1:
            c_text = self.sett_c_params(c_text, c_params)
            c_text = self.set_x_items(c_text, x_items)
            # doppia sostituzione
            # se c_text=%%text%% x_text sostituisce %text$ che diventa %new_text%
            # Es:
            # c_text=%%text%% e x_text=pippo => c_text=%pippo%
            c_text, is_replace = self.set_text_in_c_text(c_text, x_text)
            # se c_text modificato dalla seconda sosituzione allora x_text=''
            if is_replace:
                x_text = ''
            # setta nuovamente c_text utilizzando c_params
            c_text = self.sett_c_params(c_text, c_params)
        html_text = x_text+c_text
        html_data = {
            'tag': c_tag,
            'attrs': html_attrs,
            'text': html_text,
            'tail': x_tail
        }
        log_info.log(">>2 c_text").prn(0)
        log_info.log(c_text).prn(0)
        log_info.log(">> x_text").prn(0)
        log_info.log(x_text).prn(0)
        log_info.log(">>2 html_attrs").prn(0)
        log_info.log(html_attrs).prn(0)
        log_info.log(">> html_data").prn(0)
        log_info.log(pp(html_data)).prn(0)
        # ERRORi nella gestione del files csv dei tag html
        # csv_ctrl_tag == cvs_tag+"_x_"
        # csv_ctrl_tag == cvs_tag+"_xy_"
        if self.csv_tag_ctrl.find('_x') > -1:
            log_csv_err.log(f"ERROR  {self.xml_path} build_html_data()")
            log_csv_err.log(f"csv_tag_ctrl:{self.csv_tag_ctrl}")
            log_csv_err.log("x_data:", ppx(x_data))
            log_csv_err.log("h_data:", pp(html_data))
            # ultimo tag w prima dell'ERRORe
            tag_w_last = self.get_tag_w_last()
            log_csv_err.log("last w: ", tag_w_last)
            log_csv_err.log(os.linesep)
            inp.inp("?", "!")
        return html_data

    # verifica se . ! ? da seguire con una maiuscola
    def is_pc_to_up(self, x_data):
        x_tag = x_data['tag']
        pc_active = False
        if self.w_liv == 0 and x_tag == 'w':
            self.w_liv = x_data['liv']
        if x_tag == 'pc':
            t = x_data['text'].strip()
            if t in ['.', '?', '!']:
                pc_active = True
        return pc_active

    # gestione delle maiuscole dopo un . ! ?
    def after_pc(self, x_data, h_data, text, tail):
        x_liv = x_data['liv']
        x_tag = x_data['tag']
        if x_tag == 'w':
            self.w_liv = x_liv
            if text.strip() != '':
                text = text.capitalize()
                self.w_liv = 100
        h_tag = h_data['tag']
        if x_liv > self.w_liv and h_tag != 'XXX':
            if text.strip() != '':
                # text='X'+text
                text = text.capitalize()
                self.w_liv = 100
            elif tail.strip() != '':
                tail = 'Y'+tail
                # tail=tail.capitalize()
                self.w_liv = 100
        return text, tail

    #def apped_html_data(self, nd):
    def apped_html_data(self, x_data):
        """
        estrae da nd x_data
        invoca remove_params_null()
        setta:h_data
        utilizza self.hb (HtmlBuildr) per costruire HTML
        popola self.hb
        Args:
            nd (xml.node): nodo xml
        """
        #x_data = self.get_node_data(nd)
        # self.x_data_lst.append(x_data)

        x_liv = x_data['liv']
        x_is_parent = x_data['is_parent']
        x_tag = x_data['tag']

        # setta dati per tag html
        h_data = self.build_html_data(x_data)
        h_tag = h_data['tag']
        h_text = h_data['text']
        h_tail = h_data['tail']
        h_attrs = h_data['attrs']

        # FIXME se il precedente è un parent contenitor
        prev_is_container = self.is_container_stack[x_liv-1]
        if prev_is_container:
            set_trace()
            # rimpiazza text nel tag precdente (il container)
            content = f'<{h_tag} {h_attrs}>{h_text}</{h_tag}>{h_tail}'
            s = self.hb.node_last()
            content = s.replace('%text%', content)
            self.hb.upd_tag_last(content)
            # setta con XXX perrimuovere da aggiungere in quanto
            # è stato inserito nel contente del parent
            h_tag = 'XXX'

        # gestione interpretativa
        if self.dipl_inter == 'i':
            h_text = h_text.lower()
            h_tail = h_tail.lower()
            if self.is_pc_to_up(x_data) :
                h_text, h_tail = self.after_pc(x_data, h_data, h_text, h_tail)

        # popola self.hb
        if h_tag is None:
            msg = f"ERROR {self.xml_path}  xml_tag:{x_tag}  htlm is null"
            log_err.log(msg)
            log_err.log(pp(x_data))
            inp.inp("?", "!")
            return

        if x_is_parent:
            self.hb.opn(x_liv, h_tag, h_attrs, h_text, h_tail)
        else:
            self.hb.ovc(x_liv, h_tag, h_attrs, h_text, h_tail)

        log_info.log("..................").prn(0)
        log_info.log(self.hb.node_lst_last(4)).prn(0)

        if DEBUG_HTML:
            x = inp.help(f"{x_tag} (h 1..n) ")
            if x == 'h':
                print("----------------")
                print(self.hb.html_format())
                print("----------------")
            elif x.isnumeric():
                print(f"................. {x}")
                print(self.hb.node_lst_last(int(x)))
                print("................")

    def set_html_pramas(self, html):
        """utilizzando il file json formatta i parametri residui
            es. il nome del manoscrittp _MAN_
            qualsiasi altro parametro definito nel file cid configurazione
            al tag html_params
        Args:
            html (str): html
        Returns:
            html (str): html con settati i parametri         """
        params = self.html_cfg.get("html_params", {})
        for k, v in params.items():
            html = html.replace(k, v)
        return html

    def check_html(self):
        """ controlla tutte le righe htnl di HtmlBuilder
        per verificare che vi sda qualche parametro
        del tipo %param% non settato
        """
        ptrn = r"%[\w/,;:.?!^-]+%"
        lst = self.hb.tag_lst
        #le = len(lst)
        for i, row in enumerate(lst):
            ms = re.search(ptrn, row)
            if not ms is None:
                log_html_err.log(f"ERROR {self.xml_path}  check_tml()")
                log_html_err.log(f"parametro: {ms.group()}")
                log_html_err.log(f"row: {i}")
                log_html_err.log(row.strip())
                log_html_err.log("---------------------")
                log_html_err.log(os.linesep)
                inp.inp('?', '!')

    # TODO solo per i test
    def default_conf(self, wtn, di):
        self.html_cfg = {
            "html_params": {
                "_MAN_": wtn,
                "text_null": "",
                "_QA_": "\"",
                "_QC_": "\""
            },
            "html_tag_file": "teimcfg/html.csv",
            "html_tag_type": di+":txt",
            "dipl_inter": di,
            "before_id": 'K'
        }
        try:
            log_conf.log(pp(self.html_cfg).replace("'", '"')).prn(0)

            # hrml dipl./inter
            self.dipl_inter = self.html_cfg.get("dipl_inter", None)
            if self.dipl_inter is None or self.dipl_inter not in ['d', 'i']:
                raise Exception(f"ERROR dipl_inter: {self.dipl_inter}")

            # prefisso di id per diplomatia e interpretativa
            self.before_id = self.html_cfg.get("before_id", None)
            if self.before_id is None:
                raise Exception("ERROR before_id is null.")

            csv_path = self.html_cfg.get("html_tag_file", None)
            if csv_path is None:
                raise Exception("ERROR html_tag_file is null.")

            # type : d:txt d:syn i:txt i:syn
            html_tag_type = self.html_cfg.get("html_tag_type", None)
            if html_tag_type is None:
                raise Exception("ERROR html_tag_type is null.")

            self.html_tag_teimcfg = read_csv(csv_path, html_tag_type)
            log_conf.log(pp(self.html_tag_teimcfg).replace("'", '"')).prn(0)
        except Exception as e:
            log_err.log(f"ERROR {self.xml_paths}  default_conf()")
            log_err.log(e)
            ou = StringIO()
            traceback.print_exc(file=ou)
            st = ou.getvalue()
            ou.close()
            log_err.log(st)
            sys.exit(1)

    def read_conf(self, json_conf_path):
        try:
            self.html_cfg = read_json(json_conf_path)
            log_conf.log(pp(self.html_cfg).replace("'", '"')).prn(0)

            # hrml dipl./inter
            self.dipl_inter = self.html_cfg.get("dipl_inter", None)
            if self.dipl_inter is None or self.dipl_inter not in ['d', 'i']:
                raise Exception(f"ERROR dipl_inter: {self.dipl_inter}")

            # prefisso di id per diplomatia e interpretativa
            self.before_id = self.html_cfg.get("before_id", None)
            if self.before_id is None:
                raise Exception(f"ERROR before_id is null.")

            csv_path = self.html_cfg.get("html_tag_file", None)
            if csv_path is None:
                raise Exception(f"ERROR html_tag_file is null.")

            # type : d:txt d:syn i:txt i:syn
            html_tag_type = self.html_cfg.get("html_tag_type", None)
            if html_tag_type is None:
                raise Exception(f"ERROR html_tag_type is null.")
            self.html_tag_teimcfg = read_csv(csv_path, html_tag_type)
            log_conf.log(pp(self.html_tag_teimcfg).replace("'", '"')).prn(0)
        except Exception as e:
            log_err.log(f"ERROR {self.xml_path}  read_conf())")
            log_err.log(e)
            ou = StringIO()
            traceback.print_exc(file=ou)
            st = ou.getvalue()
            ou.close()
            log_err.log(st)
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
            # debug_liv = 2  # TODO
            inp.set_liv(debug_liv)

            self.x_data_lst = []
            self.xml_path = xml_path
            self.html_path = html_path
            if write_append not in ['w', 'a']:
                raise Exception(
                    f"ERROR write/append. {write_append}")

            # lettura file configurazione
            if len(conf_path) > 1:
                self.read_conf(conf_path)
            elif len(wtn) > 0 and len(dipint) > 0:
                self.default_conf(wtn, dipint)
            else:
                raise Exception(f"ERROR write_html() config is null")

            # dict dei dati xml con tag come key
            self.x_data_dict = {}
            # tag per controlo
            self.csv_tag_ctrl = ""
            self.hb.init("")



            # src = open(self.xml_path, "r").read()
            # src = src.replace("<TEI>", "")
            # src = src.replace("</TEI>", "")
            # src = "<body>"+src+"</body>"
            # parser = etree.XMLParser(ns_clean=True)
            # xml_root = etree.XML(src, parser)
            # for nd in xml_root.iter():
            #     self.apped_html_data(nd)
            xnl=XmlNodeList()
            try:
                self.x_data_lst=xnl.xml_node_data_list(self.xml_path)
            except Exception as e:
                log_err.log(e)
                sys.exit(1)
            for xd in self.x_data_lst:
                self.apped_html_data(xd)

            # chiude HTML con i tag ancora aperti
            self.hb.end()

            """gestisce il settaggio degli overflow
            modifica il parametro self.hb.tag_lst,
            """
            html_over = HtmlOvweflow(self.x_data_lst,
                                     self.hb.tag_lst,
                                     self.html_tag_teimcfg)
            html_over.set_overflow()

            # cancella o tag XX
            self.hb.del_tags('XXX')

            # controllo dei parametri %par% non settati
            self.check_html()

            # html su una riga versione per produzione
            # FIXME html = self.hb.html_onerow()
            html = self.hb.html_format()

            # setta i parametri _..._ definiti nel file <name>.json
            html = self.set_html_pramas(html)

            fu.make_dir_of_file(self.html_path)
            with open(self.html_path, write_append) as f:
                f.write("<!doctype html>"+os.linesep)
                f.write(html)
            fu.chmod(self.html_path)

        except Exception as e:
            log_err.log(f"ERROR {self.xml_path}  write_html()")
            log_err.log(e)
            ou = StringIO()
            traceback.print_exc(file=ou)
            st = ou.getvalue()
            ou.close()
            log_err.log(st)
            sys.exit(1)
        return self.html_path


def do_main(xml, html, conf_path, wtn, dipint, wa='w', deb=False):
    Xml2Html().write_html(xml, html, conf_path, wtn, dipint, wa, deb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
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

    parser.add_argument('-c',
                        dest="confpath",
                        required=False,
                        default="",
                        metavar="",
                        help="-c <file_conf.json>")

    parser.add_argument('-wt',
                        dest="wtn",
                        required=False,
                        default="",
                        metavar="",
                        help="-wt <witness>")

    parser.add_argument('-di',
                        dest="dipint",
                        required=False,
                        default="",
                        metavar="",
                        help="-di d/i (d)iplomat/i)terpret)")

    parser.add_argument('-wa',
                        dest="wa",
                        required=False,
                        metavar="",
                        default="w",
                        help="[-wa w/a] (w)rite a)ppend log.err) ")
    parser.add_argument('-d',
                        dest="deb",
                        required=False,
                        metavar="",
                        default=0,
                        help="[-d 0/1/2] (debug level)")
    args = parser.parse_args()
    do_main(args.xml,
            args.html,
            args.confpath,
            args.wtn,
            args.dipint,
            args.wa,
            args.deb)
