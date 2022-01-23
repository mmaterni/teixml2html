#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import os
import pprint
import re
from lxml import etree
from teiprjhtmlmake import LOG

__date__ = "22-01-2022"
__version__ = "0.0.1"
__author__ = "Marta Materni"


def pp(data, w=120):
    s = pprint.pformat(data, indent=2, width=w)
    return s


class XmlNodeList:

    def __init__(self):
        pass

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
            msg=f"ERROR {self.xml_path} node_tag()\n{e} "
            raise Exception(msg)

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

    def xml_node_list(self,xml_path):
        nd_lst=[]
        try:
            src = open(xml_path, "r").read()
            src = src.replace("<TEI>", "")
            src = src.replace("</TEI>", "")
            src = "<body>"+src+"</body>"
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.XML(src, parser)
            for nd in xml_root.iter():
                nd_lst.append(nd)
        except Exception as e:
            msg=f"ERROR xml_node_list()\nfile:{xml_path} \n{e}"
            raise Exception(msg)
        return nd_lst


    def xml_node_data_list(self,xml_path):
        x_data_lst=[]
        try:
            src = open(xml_path, "r").read()
            src = src.replace("<TEI>", "")
            src = src.replace("</TEI>", "")
            src = "<body>"+src+"</body>"
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.XML(src, parser)
            for nd in xml_root.iter():
                x_data=self.get_node_data(nd)
                x_data_lst.append(x_data)
        except Exception as e:
            msg=f"ERROR xml_node_data_list()\nfile:{xml_path}\n{e}"
            raise Exception(msg)
        return x_data_lst
