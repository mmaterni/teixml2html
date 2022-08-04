#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pdb import set_trace
from teimedlib.ualog import Log
import sys
import re


"""
text_start, txt_end 
parametri per il settaggio di text a inizio e fine intervallo

d|xxx|||class:xxx|%txt_start%%txt_end$|txt_start:«,txt_end:»

css_start,css_end 
parametri per il settaggio di atttrs a inizio e fine intervallo

x|damage|||class:damage%css_end%||css_end:_last

"""

TEXT_START = 'txt_start'
TEXT_END = 'txt_end'
CSS_START = 'css_start'
CSS_END = 'css_end'
CSS_FIRST_UP_LIST = ['directspeech_first_int', 'monologue_first_int']
#CSS_FIRST_UP_LIST = ['directspeech_first_int']
#CSS_FIRST_UP_LIST = ['monologue_first_int']


class HtmlOvweflow:
    """
    gestisce propriet+ overflov
    utilizzando <span from="<id>" to="<id>"  type0"<tipo>" 

    """

    def __init__(self, xml_lst, html_lst, html_conf):
        """gestione overflow
        Args:
            xml_lst (list): lista dei dati xml
            html_lst (lis): lista delle righe html
            html_conf (dict): dict del fie di configurazione csv
        """
        self.logerr = Log("w")
        self.logerr.open("log/overflow.ERR.log", 1)
        self.xml_lst = xml_lst
        self.html_lst = html_lst
        self.html_conf = html_conf
        self.span_lst = []
        self.class_w = 'class="w'
        self.class_pc = 'class="pc'
        self.trace = False

    def capitalize_first(self):
        """capitaliza 
        directspeech_first_int 
        monologue _first_int
        """
        row_last = len(self.html_lst)
        ptrn = re.compile(r"[a-z]")

        def find_text(j):
            for i in range(j, row_last):
                try:
                    row = self.html_lst[i]
                    # print(row.strip())
                    pr = row.find('>')
                    pl = row.find("</", pr)
                    if pl > -1:
                        pw = ptrn.search(row, pr)
                        if pw is not None:
                            a = pw.start()
                            b = pw.end()
                            s = row[a:b]
                            # print(a,b,s)
                            # print(row[:a])
                            # print(row[b:])
                            s = row[:a]+row[a].upper()+row[b:]
                            # print(s.strip())
                            # input("?")
                            self.html_lst[i] = s
                            break
                    if row.find("</div>") > -1:
                        break
                except IndexError as e:
                    self.logerr.log("ERROR. capitalize_first() ")
                    self.logerr.log(e)
                    self.logerr.log(row)
                    # sys.exit(1)

        for clazz in CSS_FIRST_UP_LIST:
            for i in range(0, row_last):
                row = self.html_lst[i]
                if row.find(clazz) > -1:
                    find_text(i)

    def fill_span_list(self):
        for x_data in self.xml_lst:
            x_tag = x_data.get('tag', '')
            if x_tag == 'span':
                x_items = x_data.get('items', {})
                if not "from" in x_items.keys():
                    continue
                x_from = x_items.get('from', "")
                x_to = x_items.get('to', "")
                x_type = x_items.get('type', "")
                if x_from == "" or x_to == "" or x_type == "":
                    self.logerr.log("ERROR. fill_span_list ()").prn()
                    self.logerr.log(pp(x_data)).prn()
                    sys.exit()
                item = {
                    "id0": x_from,
                    "id1": x_to,
                    "type": x_type
                }
                self.span_lst.append(item)

    def text_format(self, text, keys, pars):
        """settta pars su text
        vengono coniserati tutti gli elemnti di text dell
        pattern [%]\\w[%] e sono rimpiazzati utilizando  
        gli item di dict pars selezionati da keys
        i parametri non trovati sono settati a ""
        Args:
            text (str): testo con parametri da settare
            keys (lsit): key di pars da utilizzare
            pars (dict): parametri per settare text
        Returns:
            str: testo formatato
        """
        params = {}
        for k in keys:
            v = pars.get(k, '')
            params[k] = v
        
        ptrn = r"%[\w/,;:.?!^-]+%"
        ms = re.findall(ptrn, text)
        ks = [x.replace('%', '') for x in ms]
        for k in ks:
            v = params.get(k, '')
            text = text.replace(f'%{k}%', v)
        return text

    def add_html_class(self, flag, html_row, span_type):
        """ aggiunge una classe alle righe html in funzione del flag
        e del type

        <span from="Gl23w1" to="Gl98w6" type="directspeech"/>

        modifica da from a to secondo type

        <div class="w aggl" id="dGl2w1">Si</div>s

        <span class="pc_e gggl d" id="dGl44pc1">,</span>

        Args:
            flag (int):  flga per inizio e fine intervallo (0,1,2)
            html_row (str): riga html
            span_type (str): tipo span from to
        Returns:
            str: riga html modificata
        """
        try:
            c_data = self.html_conf.get(span_type, None)
            if c_data is None:
                raise Exception(
                    f"attr_type:{span_type} ERROR csv row not found ")
            c_attrs = c_data.get('attrs', {})
            css_class = c_attrs.get('class', "css_err")
            c_text = c_data.get('text', "")
            c_params = c_data.get('params', {})
            #FIXME TEXT_START e TEXT_END probabilmente INUILI testare
            if c_text.find('%') > -1:
                if flag == 0:
                    c_text = self.text_format(c_text, [TEXT_START], c_params)
                elif flag == 2:
                    c_text = self.text_format(c_text, [TEXT_END], c_params)
                else:
                    c_text = self.text_format(c_text, [], {})
            if css_class.find('%') > -1:
                if flag == 0:
                    css_class = self.text_format(css_class, [CSS_START], c_params)
                elif flag == 2:
                    css_class = self.text_format(css_class, [CSS_END], c_params)
                else:
                    css_class = self.text_format(css_class, [], {})

            p0 = html_row.find(self.class_w)
            if p0 > -1:
                p0 = p0+len(self.class_w)
            else:
                p0 = html_row.find(self.class_pc)
                if p0 > -1:
                    p0 = p0+len(self.class_pc)
            if p0 < 0:
                raise Exception("ERROR in html not found tag w or pc")
            p1 = html_row.find('"', p0)
            s = html_row[0:p1]+" "+css_class+html_row[p1:]

            # FIXME IUTILE aggiunge eventuale testo a inizio e fine
            # utilizzato per directspeech e monologue
            if c_text != '':
                if flag == 0:
                    s = s.replace('>', f'>{c_text}', 1)
                elif flag == 2:
                    if s.find('</') > -1:
                        s = s.replace('</', f'{c_text}</', 1)
                    else:
                        s = f'{s}{c_text}'
            return s
        except Exception as e:
            self.logerr.log("ERROR. add_html_class() ")
            self.logerr.log(e)
            self.logerr.log(html_row)
            sys.exit(1)

    def set_html(self, from_to):
        """setta le righe html comprese nellìintervallo from to
        Args:
            from_to (str): intervallo degli id delle classi w e pc
        """

        def find_w_id(r, id):
            ptr_id = f'{id}"'
            p = r.find(ptr_id)
            return p > -1

        def find_w_pc(rh):
            p = rh.find(self.class_w)
            if p < 0:
                p = rh.find(self.class_pc)
            return p > -1

        id_from = from_to['id0']
        id_to = from_to['id1']
        span_type = from_to['type']
        flag = 0
        for i, html_row in enumerate(self.html_lst):
            if flag == 0:
                # verifica se è  word o pc
                if find_w_pc(html_row):
                    # cerca nella riga id_form
                    if find_w_id(html_row, id_from):
                        # setta come inizio (flga=0)
                        row = self.add_html_class(0, html_row, span_type)
                        self.html_lst[i] = row
                        flag = 1
                        continue
            if flag == 1:
                # verifica se è  word o pc
                if find_w_pc(html_row):
                    # cerca nella riga id_to
                    if find_w_id(html_row, id_to):
                        # setta word o pc com fine (flag=2)
                        row = self.add_html_class(2, html_row, span_type)
                        self.html_lst[i] = row
                        flag = 3
                        break
                    # setta word o pc nell'intervallo (flag==1)
                    row = self.add_html_class(1, html_row, span_type)
                    self.html_lst[i] = row
        if flag == 0:
            # errroe nlla gestione inizio gine
            self.logerr.log("ERROR. set_html()")
            self.logerr.log(f"{id_from} {id_to}  {span_type}   Not Found")

    def set_overflow(self):
        self.fill_span_list()
        for x_data in self.span_lst:
            self.set_html(x_data)
        self.capitalize_first()
