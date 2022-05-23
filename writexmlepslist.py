#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
from syslog import LOG_ERR
from lxml import etree
import os
import argparse
import sys
import pprint
import pathlib as pl
from teimedlib.ualog import Log
from teimedlib.xml_const import *

__date__ = "22-05-2022"
__version__ = "0.0.1"
__author__ = "Marta Materni"


logerr = Log("w")

def pp(data, w=40):
    s = pprint.pformat(data, indent=0, width=w)
    return s

class WriteXmlEpisodes:

    def __init__(self, dir_in, dir_out, sigla_man):
        self.dir_in = dir_in
        self.dir_out = dir_out
        self.sigla_man = sigla_man
        path_err = os.path.join(dir_out, "split_ERR.log")
        logerr.open(path_err, liv=1)
  
    def node_tag(self, nd):
        try:
            tag = nd.tag
            tag = tag if type(nd.tag) is str else "XXX"
            pid = tag.find('}')
            if pid > 0:
                tag = tag[pid + 1:]
            return tag.strip()
        except Exception as e:
            logerr.log("ERROR in xml")
            logerr.log(str(e))
            return "XXX"

    def get_notes(self, root):
        back = root.find("back")
        if back is None:
            return ""
        note = back.find('div')
        nds = note.findall('teimed_note')
        ls = []
        for nd in nds:
            xml_node = etree.tostring(nd,
                                      method='xml',
                                      xml_declaration=None,
                                      encoding='unicode',
                                      with_tail=True,
                                      pretty_print=True)
            ls.append(xml_node.strip())
        s = "".join(ls)
        return s

    
    def node_src(self, nd):
        tag = nd.tag
        ks = self.node_attrs(nd)
        s = "<" + tag
        for k in ks:
            if k=='id':
                continue
            v = ks[k]
            s = s + ' %s="%s"' % (k, v)
        s = s + " />"
        return s

    def node_attrs(self, nd):
        attrs = {}
        if nd.attrib is None:
            return attrs
        for k, v in nd.attrib.iteritems():
            px = k.find('}')
            if px > -1:
                k = k[px + 1:]
            attrs[k] = v
        return attrs


    def write_episode_lst(self):
        p = pl.Path(self.dir_in)
        eps_path_lst = sorted(list(p.glob("*.xml")))
        lst=[TEI_TOP]
        for eps_path in eps_path_lst:
            name=eps_path.name.replace(".xml","")
            if name==self.sigla_man:
                continue
            path_abs = f"{eps_path.absolute()}"
            try:
                src = open(path_abs, "r").read()
                parser = etree.XMLParser(ns_clean=True)
                xml_root = etree.XML(src, parser)
            except Exception as e:
                msg = f"ERROR \n{eps_path} \n{e}"
                logerr.log(msg)
                sys.exit()
            for nd in xml_root.getiterator():
                tag=self.node_tag(nd)
                if tag == "div":
                    ks = self.node_attrs(nd)
                    tp = ks.get('type', "x")
                    if tp == "episode":
                        # <div type="episode" ref="#ep12" />
                        src = self.node_src(nd)
                        lst.append(src)
                        break
        notes=self.get_notes(xml_root)
        lst.append(notes)
        lst.append(TEI_BOTTOM)
        xml="".join(lst)
        path_out=os.path.join(self.dir_out,f"{self.sigla_man}.xml")
        with open(path_out,"w") as f:
            f.write(xml)

def do_main(path_in, dir_out, sigla_man):
    xmlspl = WriteXmlEpisodes(path_in, dir_out, sigla_man)
    xmlspl.write_episode_lst()


if __name__ == "__main__":
    """
    es.
    dir input: xml/par
    dir out  : xml/par
    sigla_man: par
    """
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    parser.add_argument(
        '-i',
        dest="src",
        required=True,
        metavar="",
        help="-i <dir input ./xml/sigla")
    parser.add_argument(
        '-o',
        dest="ou",
        required=True,
        metavar="",
        help="-o <dir out ./xml/<sigla>")
    parser.add_argument(
        '-m',
        dest="man",
        required=True,
        metavar="",
        help="-m <sigla_maoscritto>")
    args = parser.parse_args()
    do_main(args.src, args.ou, args.man)
