#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import os
import sys
from teimedlib.ualog import Log
import traceback
TAG_COL_NUM = 12
XML_TAG_INTEST="xml_tag"

logerr = Log("w")
logerr.open("log/readhtmlconf.ERR.log", 1)


def t_split(s):
    sp = s.split(':')
    s0 = sp[0]
    le = len(sp)
    if le > 1:
        s1 = sp[1]
    else:
        s1 = ''
    return s0, s1

    """
    d : diplomatica         text + syn
    i : interpretativa      text + syn
    xt: dipp + inter        text
    xs: dipp + inter               syn
    dt: dip                 text 
    ds: dip                        syn
    it:         inter       text
    d:          inter              syn
        d   i   xt  xs  dt  ds  it  is
    x   1   1   1   1   1   1   1   1
    
    d   1   0   1   1   1   1   0   0
    i   0   1   1   1   0   0   1   1
    
    xt  0   0   1   0   1   0   1   0
    xs  0   0   0   1   0   1   0   1
    
    dt  0   0   1   0   1   0   0   0
    ds  0   0   0   1   0   1   0   0

    it  0   0   1   0   0   0   1   0
    is  0   0   0   1   0   0   0   1
    
    """
def row_ok(t, e):
    if t == 'x'or t == e:
        return True
    e0, e1 = t_split(e)
    if t.find(':') < 0:
        if t == e0 or e0=='x':
            return True
    else:
        t0, t1 = t_split(t)
        if t0 == 'x' and t1==e1:
            return True
        if e0 == 'x'  and t1==e1:
            return True
    return False

# x|xml_tag|tag|keys|attrs|text|params|parent!tags|before|after
def cvs2json(csv, html_tag_type):
    lsb = ["", "", "", "", "", "", "", ""]
    js = {}
    for row in csv:
        if row.strip() == "":
            continue
        try:
            row_data = {}
            #TODO row = row.replace(os.linesep, '')
            flds = row.split('|')
            if len(flds) < TAG_COL_NUM:
                le = len(flds)
                flds.extend(lsb[0:TAG_COL_NUM-le])
            x = flds[0]
            if row_ok(x,html_tag_type) is False:
                continue

            flds = flds[1:]
            xml_tag = flds[0]
            # salta righe di intestazione
            if xml_tag == XML_TAG_INTEST:
               continue

            flds = [x.strip() for x in flds]
            #   0     1   2     3    4     5        6         7     8
            #xml_tag|tag|keys|attrs|text|params|parent!tags|before|after

            # tag
            tag = flds[1]
            row_data['tag'] = tag
            # keys  []
            f = flds[2]
            if f != '':
                keys = f.split(',')
                row_data['keys'] = keys
            # attrs {}
            f = flds[3]
            if f != '':
                ls = f.split(',')
                attrs = {}
                for x in ls:
                    kv = x.split(':')
                    if len(kv) !=2 :
                        logerr.log("tags_cvs2json() 1")
                        logerr.log(f'csv in column attrs; field:{f}\n')
                        logerr.log(row)
                        sys.exit()
                    k=kv[0]
                    v=kv[1]
                    attrs[k] = v
                row_data['attrs'] = attrs
            # text=""
            f = flds[4]
            if f != '':
                row_data['text'] = f
            # params
            f = flds[5]
            if f != '':
                ls = f.split(',')
                params = {}
                for x in ls:
                    kv = x.split(':')
                    if len(kv) !=2 :
                        logerr.log("tags_cvs2json() 2")
                        logerr.log(f'ERROR csv in column params; field:{f}\n')
                        logerr.log(row)
                        sys.exit()
                    k=kv[0]
                    v=kv[1]
                    params[k] = v
                row_data['params'] = params
            # parent
            f = flds[6]
            if f != '':
                row_data['parent'] = f
            
            js[xml_tag] = row_data
        except Exception as e:
            s = traceback.format_exc()
            logerr.log("ERROR tags_cvs2json() 3")
            logerr.log(str(e))
            logerr.log(s)
            logerr.log(row)
            sys.exit(1)
    return js


# def read_csv(csv_path, html_tag_type):
#     with open(csv_path, "r+") as f:
#         csv = f.readlines()
#     js = cvs2json(csv, html_tag_type)
#     return js


def read_csv(csv_path, html_tag_type):
    with open(csv_path, "r") as f:
        txt = f.read()
    txt=txt.replace(f"\{os.linesep}","")
    csv=txt.split(os.linesep)
    js = cvs2json(csv, html_tag_type)
    return js
