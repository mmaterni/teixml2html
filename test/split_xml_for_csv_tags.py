#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
import os
import pprint
from teimedlib.xml_node_list import XmlNodeList
import teimedlib.pathutils as ptu
from lxml import etree

#__date__ = "22-03-2022"
#__version__ = "0.0.7"

"""
popola xml_test
"""

def pp(data, w=120):
    s = pprint.pformat(data, indent=2, width=w)
    return s


class SplitXml:

    def __init__(self):
        self.xnl = XmlNodeList()
        self.xml_lst = []

    # x|xml_tag|tag|keys|attrs|text|params|parent
    def read_csv(self, csv_path, di):
        xdi = [di,'x']
        with open(csv_path, "r") as f:
            txt = f.read()
        txt = txt.replace(f"\{os.linesep}", "")
        csv = txt.split(os.linesep)
        lst = []
        for row in csv:
            if row.strip() == '':
                continue
            if row[0] not in xdi:
                continue
            fs = row.split('|')
            #tps = fs[0]
            tag = fs[1]
            if tag == 'xml_tag':
                continue
            lst.append(tag)
        return sorted(lst)

    def xml_list(self, nd_lst):
        xml_lst = []
        for nd in nd_lst:
            x_data = self.xnl.get_node_data(nd)
            tag = x_data['tag']
            if tag in ['l', 'p']:
                xml = etree.tostring(nd,
                                     method='xml',
                                     xml_declaration=None,
                                     encoding='unicode',
                                     with_tail=True,
                                     pretty_print=False,
                                     standalone=None,
                                     doctype=None,
                                     exclusive=False,
                                     inclusive_ns_prefixes=None,
                                     strip_text=False)
                xml_lst.append(xml)
        return xml_lst

    def find_tag_in_xml_list(self, tag):
        xml = ''
        for x in self.xml_lst:
            if x.find(f"<{tag}") > -1:
                xml = x
                break
        return xml

    def find_attr_in_xml_list(self, tag_attr):
        sp = tag_attr.split('+')
        tag = sp[0]
        attr = sp[1:]
        xml = ''
        for x in self.xml_lst:
            s = x.replace(os.linesep, "")
            if (pt := s.find(f"<{tag}")) > -1:
                le = len(attr)
                if le == 1:
                    if (p0 := s.find(attr[0], pt)) > -1:
                        xml = x
                elif le == 2:
                    if (p0 := s.find(attr[0], pt)) > -1:
                        if (p1 := s.find(attr[1], pt)) > -1:
                            xml = x
                elif le == 3:
                    if (p0 := s.find(attr[0], pt)) > -1:
                        if (p1 := s.find(attr[1], pt)) > -1:
                            if (p2 := s.find(attr[2], pt)) > -1:
                                xml = x
                else:
                    print(f"warning {tag_attr}")
                    input("?")
            if xml != '':
                break
        return xml

    def write_xml_for_tag(self, tag_lst, d_i):

        def xml_div(x):
            s=f"<div>\n{x}</div>"
            return s

        # tag senza +
        for tag in tag_lst:
            p = tag.find('+')
            if p > -1:
                continue
            #print(tag)
            # trova il segmento xml che contiee il tag
            xml = self.find_tag_in_xml_list(tag)
            if xml != '':
                # trovaro
                pth = F"xml_test/{d_i}/{tag}.xml"
                s=xml_div(xml)
                #AAA fu.write_path_file(pth,s)
                ptu.make_dir_of_file(pth)
                with open(pth,"w") as f:
                    f.write(s)
            else:
                # non esiste un segmento xm che contenga il tag
                pth = F"xml_test/{d_i}_null/{tag}.xml"
                #AAA fu.write_path_file(pth,"null")
                ptu.make_dir_of_file(pth)
                with open(pth,"w") as f:
                    f.write("null")

        # tag con +
        for tag in tag_lst:
            p = tag.find('+')
            if p < 0:
                continue
            #print(tag)
            xml = self.find_attr_in_xml_list(tag)
            tag_attr = tag.replace('+', '_')
            if xml != '':
                #trovato
                pth = F"xml_test/{d_i}/{tag_attr}.xml"
                s=xml_div(xml)
                #AAA fu.write_path_file(pth,s)
                ptu.make_dir_of_file(pth)
                with open(pth,"w") as f:
                    f.write(s)
            else:
                #non trovato
                pth = F"xml_test/{d_i}_null/{tag_attr}.xml"
                #AAA fu.write_path_file(pth,"null")
                ptu.make_dir_of_file(pth)
                with open(pth,"w") as f:
                    f.write(s)

    def split_xml(self, xml_path):
        # per ogni nodo costruisce un segmento completo xml
        nd_lst = self.xnl.xml_node_list(xml_path)
        self.xml_lst = self.xml_list(nd_lst)
        
        # lettura tagd csv
        tag_path = "teimcfg/html.csv"
        tag_dip_lst = self.read_csv(tag_path, "d")
        tag_int_lst = self.read_csv(tag_path, "i")
        
        # per ogni tag trova il segmento xml 
        # che lo contiene e lo scrive
        self.write_xml_for_tag(tag_dip_lst,"dipl")
        self.write_xml_for_tag(tag_int_lst, "inter")


def do_main(xp):
    spx = SplitXml()
    spx.split_xml(xp)


if __name__ == "__main__":
    le=len(sys.argv)
    if le==1:
        print("")
        print("split_xml_for_csv_tags.py  <file_name.xml>")
        sys.exit()
    xp = sys.argv[1]
    #xp = "xml/floripar.xml"
    do_main(xp)
