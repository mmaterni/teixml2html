#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import os
import pprint
import re
from lxml import etree
from teiprjhtmlmake import LOG

__date__ = "27-05-2022"
__version__ = "0.0.3"
__author__ = "Marta Materni"


def pp(data, w=60):
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
            msg = f"ERROR {self.xml_path} node_tag()\n{e} "
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
        id_ = self.node_id(nd)
        liv = self.node_liv(nd)
        tag = self.node_tag(nd)
        # evita val troppo grandi
        if liv < 2:
            val = ''
        else:
            val = self.node_val(nd)
            if len(val) > 1000:
                val = ''

        if id_ != '':
            id_num = self.node_id_num(id_)
            items['id_num'] = id_num
        return {
            'id': id_,
            'liv': liv,
            'tag': tag,
            'text': self.node_text(nd),
            'tail': self.node_tail(nd),
            'items': items,
            # 'keys': self.node_keys(nd),
            'val': val,
            'is_parent': self.node_is_parent(nd)
        }

    def xml_node_list(self, xml_path):
        nd_lst = []
        try:
            src = open(xml_path, "r").read()
            # src = src.replace("<TEI>", "")
            # src = src.replace("</TEI>", "")
            # src = "<body>"+src+"</body>"
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.XML(src, parser)
            for nd in xml_root.iter():
                nd_lst.append(nd)
        except Exception as e:
            msg = f"ERROR xml_node_list()\nfile:{xml_path} \n{e}"
            raise Exception(msg)
        return nd_lst

    def lb2l(self, xml_path):
        with open(xml_path, "r") as f:
            rows = f.readlines()
        lb_idxs = []
        end_idx = 0
        for i, row in enumerate(rows):
            if row.find("<lb/>") > -1:
                lb_idxs.append(i)
            if row.find("</>"):
                end_idx = i
            if row.find("</pc>"):
                end_idx = i

        i = lb_idxs[0]
        rows[i] = rows[i].replace("<lb/>", "<l>")
        for i in lb_idxs[1:]:
            rows[i] = rows[i].replace("<lb/>", "</l><l>")
        rows[end_idx] = rows[end_idx]+"</l>"

        src = "".join(rows)
        open("pippo.xml", "w").write(src)
        return src

    def xml_node_data_list(self, xml_path):
        self.lb2l(xml_path)
        x_data_lst = []
        try:
            src = open(xml_path, "r").read()
            # src = src.replace("<TEI>", "<div>")
            # src = src.replace("</TEI>", "</div>")
            # src = "<body>"+src+"</body>"
            parser = etree.XMLParser(ns_clean=True)
            xml_root = etree.XML(src, parser)
            for nd in xml_root.iter():
                x_data = self.get_node_data(nd)
                liv = x_data.get("liv")
                # AAA controllo sul livello < 2
                if liv < 2:
                    continue
                x_data_lst.append(x_data)
        except Exception as e:
            msg = f"ERROR xml_node_data_list()\nfile:{xml_path}\n{e}"
            raise Exception(msg)
        return x_data_lst
